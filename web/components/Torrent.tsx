import * as React from "react";


export interface TorrentProps {
    //onWatch: (infoHash: string) => void;
    onRemove: (infoHash: string) => void;
    infoHash: string;
    name: string;
    progress: string;
    pieces: number[];
}


export interface TorrentState {
}


export class Torrent extends React.Component<TorrentProps, TorrentState> {

    constructor(props: Readonly<TorrentProps>) {
        super(props)

        this.state = { };
    }

    handleClickRemove(event: React.MouseEvent) {
        event.preventDefault();
        let infoHash = this.props.infoHash;
        this.props.onRemove(infoHash);
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