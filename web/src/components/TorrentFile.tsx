import * as React from "react";


export interface TorrentFileProps {
    infoHash: string;
    idx: string;
    name: string;
    size: string;
    mimeType: string;
}


export interface TorrentFileState {
    
}


export class TorrentFile extends React.Component<TorrentFileProps, TorrentFileState> {

    constructor(props: Readonly<TorrentFileProps>) {
        super(props)

        this.state = { };
    }

    render() {
        return (
            <div>
                <h5>{this.props.name}</h5>({this.props.size})
                {this.props.mimeType.startsWith("video") &&
                    <a className="button" href={`/watch/${this.props.infoHash}/${this.props.idx}`}>Watch</a>
                }
            </div>
        );
    }
}