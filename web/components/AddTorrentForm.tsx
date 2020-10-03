import * as React from "react";


interface AddTorrentFormProps {
    onAddTorrent: (data: string, encoding: string) => void;
}


interface AddTorrentFormState {
    displayData: string;
    data: string;
}


export class AddTorrentForm extends React.Component<AddTorrentFormProps, AddTorrentFormState> {

    constructor(props: Readonly<AddTorrentFormProps>) {
        super(props);
        this.state = { displayData: "", data: "" };
    }

    handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ displayData: event.target?.value, data: event.target?.value });
    }

    handleFileSelected(event: React.ChangeEvent<HTMLInputElement>) {
        const reader = new FileReader()
        let selectedFile = event.target?.files[0];
        this.setState({ displayData: event.target?.value });
        reader.onload = (e) => {
            let data = e.target?.result as string;
            this.setState({ data });
        }
        reader.readAsDataURL(selectedFile);
    }

    handleSubmit(event: MouseEvent) {
        event.preventDefault();
        let data = this.state.data;
        let encoding = this.state.data === this.state.displayData ? "none" : "base64";
        this.props.onAddTorrent(data, encoding);
    }

    render() {
        return (
            <div>
                <input type="text" value={this.state.displayData} onChange={this.handleChange.bind(this)} />
                <label htmlFor="selectFile">...</label>
                <input id="selectFile" type="file" onChange={this.handleFileSelected.bind(this)} style={{display: "none"}}/>
                <button onClick={this.handleSubmit.bind(this)}>Add</button>
            </div>
        );
    }
}