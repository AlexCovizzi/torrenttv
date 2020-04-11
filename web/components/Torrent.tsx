import * as React from "react";
import { TorrentFile } from "./TorrentFile";


export interface TorrentProps {
    //onWatch: (infoHash: string) => void;
    onRemove: (infoHash: string, deleteFiles: boolean) => void;
    infoHash: string;
    name: string;
    progress: string;
    pieces: number[];
}


export interface TorrentState {
    deleteFiles: boolean;
    showFiles: boolean;
    files: any[];
}


export class Torrent extends React.Component<TorrentProps, TorrentState> {

    constructor(props: Readonly<TorrentProps>) {
        super(props)

        this.state = { deleteFiles: false, showFiles: false, files: [] };
    }

    handleClickShowFiles(event: React.MouseEvent) {
        event.preventDefault();
        let showFiles = this.state.showFiles;
        this.setState({showFiles: !showFiles});

        if (this.state.files.length === 0) {
            this.fetchFiles();
        }
    }

    handleClickRemove(event: React.MouseEvent) {
        event.preventDefault();
        let infoHash = this.props.infoHash;
        let deleteFiles = this.state.deleteFiles;
        this.props.onRemove(infoHash, deleteFiles);
    }

    handleChangeCheckbox(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ deleteFiles: event.target?.checked });
    }

    fetchFiles() {
        fetch(`/api/v1/session/torrents/${this.props.infoHash}/files`, {
            credentials: 'same-origin',
            mode: 'same-origin',
            method: "GET",
        })
        .then(res => {
            if (res.status == 200) {
                return res.json()
            } else {
                return Promise.reject(res)
            }
        }).then(json => {
            console.log(json.list);
            this.setState({
                files: json.list
            })
        }).catch((err) => {
            console.error(err);
        });
    }

    render() {
        const progressPercentage = Number.parseFloat(this.props.progress) * 100
        return (
            <div>
                <h4 title={this.props.name}>{this.props.name}</h4>
                <div title={progressPercentage.toFixed(2) + "%"}>
                    <Pieces pieces={this.props.pieces}></Pieces><br/>
                </div>
                <a className="button" href={`/watch/${this.props.infoHash}`}>Watch</a>
                <a className="button is-danger" onClick={this.handleClickRemove.bind(this)}>Remove</a>
                <label className="checkbox">
                    <input type="checkbox" onChange={this.handleChangeCheckbox.bind(this)} />
                    Delete files
                </label>
                <button className="button" onClick={this.handleClickShowFiles.bind(this)}>Show Files</button>
                {this.state.showFiles &&
                    <div>
                        {this.state.files.map((file, idx) =>
                            <TorrentFile key={idx} idx={idx} infoHash={this.props.infoHash} {...file}></TorrentFile>
                        )}
                    </div>
                }
                
            </div>
        );
    }
}


const Pieces: React.SFC<{pieces: number[]}> = (props) => {
    let piecesSplit = splitUp(props.pieces, 100);
    let pieceColorList = piecesSplit.map((pieceGroup) => {
        let numTrue = 0;
        for (let p of pieceGroup) {
            numTrue += p ? 1 : 0;
        }
        let percent = (numTrue / pieceGroup.length) * 100;
        let color = `hsl(120, 100%, ${(100-percent/2).toFixed(0)}%)`;
        return color;
    });
    return (
        <svg viewBox="0 0 100 4" style={{border: "1px solid #444"}}>
            {pieceColorList.map((pieceColor, idx) =>
                <line x1={idx} y1="0" x2={idx} y2="4" style={{stroke: pieceColor, strokeWidth: 1}} />
            )}
        </svg>
    );
}


function splitUp<T>(arr: T[], n: number) {
    let rest = arr.length % n, // how much to divide
        restUsed = rest, // to keep track of the division over the elements
        partLength = Math.floor(arr.length / n),
        result = [];

    for(let i = 0; i < arr.length; i += partLength) {
        let end = partLength + i, add = false;

        if(rest !== 0 && restUsed) { // should add one element for the division
            end++;
            restUsed--; // we've used one division element now
            add = true;
        }

        result.push(arr.slice(i, end)); // part of the array

        if(add) {
            i++; // also increment i in the case we added an extra element for division
        }
    }

    return result;
}