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
                        <th>Name</th>
                        <th>Size</th>
                        <th>Seeds</th>
                        <th>Download</th>
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