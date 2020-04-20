import * as React from "react";


interface SearchFormProps {
    onSubmit: (query: string) => void;
}


interface SearchFormState {
    query: string;
}


export class SearchForm extends React.Component<SearchFormProps, SearchFormState> {

    constructor(props: Readonly<SearchFormProps>) {
        super(props);
        this.state = { query: "" };
    }

    handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ query: event.target?.value });
    }

    handleSubmit(event: MouseEvent) {
        event.preventDefault();
        let query = this.state.query;
        this.props.onSubmit(query);
    }

    render() {
        return (
            <div className="field has-addons">
                <div className="control is-expanded">
                    <input className="input" type="text" value={this.state.query} onChange={this.handleChange.bind(this)} />
                </div>
                <div className="control">
                    <a className="button" onClick={this.handleSubmit.bind(this)}>Search</a>
                </div>
            </div>
        );
    }
}