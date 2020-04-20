import * as React from "react";
import { AddTorrentForm } from "./AddTorrentForm";
import { Torrent } from "./Torrent";
import { SearchResult } from "./SearchResult";
import { SearchForm } from "./SearchForm";
import { SearchResultTable } from "./SearchResultTable";


interface MainState {
    torrents: any[];
    results: any[];
}


export class Main extends React.Component<{}, MainState> {

    private intervalHandle: number;

    constructor(props: Readonly<{}>) {
        super(props);
        this.state = {torrents: [], results: []};
    }

    addTorrent(data: string) {
        const uri = data;
        fetch("/api/v1/session/torrents", {
            credentials: 'same-origin',
            mode: 'same-origin',
            method: "POST",
            body: JSON.stringify({ uri })
        })
        .then(res => {
            if (res.status == 200) {
                return res.json()
            } else {
                return Promise.reject(res)
            }
        })
    }

    removeTorrent(infoHash: string, deleteFiles: boolean) {
        fetch("/api/v1/session/torrents/" + infoHash, {
            credentials: 'same-origin',
            mode: 'same-origin',
            method: "DELETE",
            body: JSON.stringify({deleteFiles: deleteFiles})
        })
        .then(res => {
            if (res.status == 200) {
                return res.json()
            } else {
                return Promise.reject(res)
            }
        })
    }

    searchTorrents(query: string) {
        fetch(`/api/v1/search?query=${encodeURI(query)}`, {
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
            this.setState({
                results: json.list
            })
        });
    }

    fetchTorrents() {
        fetch(`/api/v1/session/torrents`, {
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
            this.setState({
                torrents: json.list
            })
        }).catch((err) => {
            console.error(err);
            clearInterval(this.intervalHandle);
        });
    }

    updateTorrent(infoHash: string, data: any) {
        fetch(`/api/v1/session/torrents/${infoHash}`, {
            credentials: 'same-origin',
            mode: 'same-origin',
            method: "PATCH",
            body: JSON.stringify(data)
        })
        .then(res => {
            if (res.status == 200) {
                return res.json()
            } else {
                return Promise.reject(res)
            }
        })
    }

    componentDidMount() {
        this.intervalHandle = setInterval(() => {
            this.fetchTorrents();
        }, 1000);
        console.log("DidMount: "+this.intervalHandle);
    }

    componentWillUnmount() {
        console.log("WillUnmount: "+this.intervalHandle);
        clearInterval(this.intervalHandle);
        this.intervalHandle = undefined;
    }

    render() {
        return (
            <div className="container">
                <div className="columns">
                    <div className="column is-two-thirds">
                        <SearchForm onSubmit={this.searchTorrents.bind(this)}></SearchForm>
                        <SearchResultTable results={this.state.results} onClick={this.addTorrent.bind(this)}></SearchResultTable>
                    </div>
                    <div className="column">
                        {this.state.torrents.map((torrent) =>
                            <Torrent key={torrent.infoHash} {...torrent}
                                onRemove={this.removeTorrent.bind(this)}
                                onPause={(infoHash) => this.updateTorrent(infoHash, {paused: true})}
                                onResume={(infoHash) => this.updateTorrent(infoHash, {paused: false})}>
                            </Torrent>
                        )}
                    </div>
                </div>
            </div>
        );
    }
}