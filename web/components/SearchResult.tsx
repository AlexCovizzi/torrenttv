import * as React from "react";
import {ArrowDownIcon, PlayIcon} from '@primer/octicons-react';


interface SearchResultProps {
    onClick: (link: string) => void;
    provider: string;
    name: string;
    size: string;
    seeds: number;
    link: string;
    infourl: string;
}


interface SearchResultState {
    //
}


export class SearchResult extends React.Component<SearchResultProps, SearchResultState> {

    constructor(props: Readonly<SearchResultProps>) {
        super(props);
        this.state = { };
    }

    handleClick(event: MouseEvent) {
        event.preventDefault();
        if (this.props.link) {
            this.props.onClick(this.props.link);
        } else {
            this.fetchLink().then((link) => {
                this.props.onClick(link);
            })
        }
    }

    fetchLink() {
        let provider = encodeURIComponent(this.props.provider);
        let infoUrl = encodeURIComponent(this.props.infourl);
        return fetch(`/api/v1/details?provider=${provider}&infourl=${infoUrl}`, {
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
        })
        .then(json => {
            return json.link;
        })
    }

    render() {
        return (
            <tr>
                <td colSpan={4} style={{wordBreak: "break-all"}}>{this.props.name}</td>
                <td className="is-norrow has-text-centered">{this.props.size}</td>
                <td className="is-norrow has-text-centered">{this.props.seeds >= 0 ? this.props.seeds : "-"}</td>
                <td className="is-norrow has-text-centered">
                    <a className="button is-small" onClick={this.handleClick.bind(this)}>
                        <span className="icon is-small"><ArrowDownIcon /></span>
                    </a>
                    <a className="button is-small">
                        <span className="icon is-small"><PlayIcon /></span>
                    </a>
                </td>
            </tr>
        );
    }
}