import { useEffect, useState} from "react";

export default function ClientDropdown( {onSelectClient}){

    const [clients, setClients] = useState([]);

    useEffect(() => {
        fetch("http://127.0.0.1:5001/notion/clients")
        .then((response) => response.json())
        .then((data) => setClients(data))
        .catch((err) => console.error("Can't fetch clients", err));
    }, []);

    return(
        <select className="flex bg-diff highlight py-4 px-3 rounded text-sm my-5 justify-between"
            onChange={(x) => onSelectClient(x.target.value)}>
                
            <option className="hidden">Select a Client:</option>
            {clients.map((client) => (
                <option key={client} value={client} > {client} </option>
            ))}
        </select>
    );
}