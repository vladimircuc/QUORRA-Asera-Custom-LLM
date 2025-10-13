import { useEffect, useState} from "react";

export default function ClientDropdown( {clients, setSelectedClient}){

    return(
        <select className="flex bg-diff highlight py-4 px-3 rounded text-sm  mt-8 mb-5 justify-between cursor-pointer"
            onChange={(x) => {
                const selectClientID = x.target.value;
                console.log("Selected client_id:", x.target.value);
                const selectClientObj = clients.find(x => x.id.toString() ===  selectClientID);
                setSelectedClient(selectClientObj)}}>
                
            <option className="hidden">Select a Client:</option>
            {clients.map((client) => (
                <option key={client.id} value={client.id} > {client.name} </option>
            ))}
        </select>
    );
}