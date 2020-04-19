import * as React from "react";
import { SearchResult } from "./SearchResult";


interface SearchResultTableProps {
    onClick: (link: string) => void,
    results: any[]
}


interface SearchResultTableState {
    //
}


export class SearchResultTable extends React.Component<SearchResultTableProps, SearchResultTableState> {

    constructor(props: Readonly<SearchResultTableProps>) {
        super(props);
        this.state = { };
    }

    render() {
        return (
            <table className="table is-fullwidth is-hoverable">
                <thead>
                    <tr>
                        <th colSpan={4} >Name</th>
                        <th className="is-norrow has-text-centered">Size</th>
                        <th className="is-norrow has-text-centered">Seeds</th>
                        <th className="is-norrow has-text-centered"></th>
                    </tr>
                </thead>
                <tbody>
                    {this.props.results.map((result) =>
                        <SearchResult {...result} onClick={this.props.onClick}></SearchResult>
                    )}
                </tbody>
            </table>
        );
    }
}