import * as React from "react";
import * as bytes from "bytes";


export interface TorrentFileProps {
    infoHash: string;
    idx: string;
    name: string;
    size: number;
    mimeType: string;
}


export interface TorrentFileState {

}


export class TorrentFile extends React.Component<TorrentFileProps, TorrentFileState> {

    constructor(props: Readonly<TorrentFileProps>) {
        super(props)

        this.state = {};
    }

    onClick() {
        fetch(`/play/${this.props.infoHash}/${this.props.name}`)
    }

    render() {
        return (
            <div>
                <h5>{this.props.name} <span>({bytes(this.props.size, { decimalPlaces: 2 })})</span></h5>
                {this.props.mimeType.startsWith("video") &&
                    <a className="button" onClick={this.onClick.bind(this)}>Play</a>
                }
            </div>
        );
    }
}