import * as React from "react";


interface SearchResultProps {
    onClick: (link: string) => void,
    provider: string,
    name: string,
    size: string,
    seeds: number,
    link: string
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
        let link = this.props.link;
        this.props.onClick(link);
    }

    render() {
        return (
            <tr>
                <td>{this.props.name}</td>
                <td>{this.props.size}</td>
                <td>{this.props.seeds >= 0 ? this.props.seeds : "-"}</td>
                <a className="button" onClick={this.handleClick.bind(this)}>&#10515;</a>
            </tr>
        );
    }
}