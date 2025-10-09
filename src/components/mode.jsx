import { useState } from "react";

export default function mode({mode, setMode}) {

  return (
    <button className="cursor-pointer" onClick={() => 
        setMode(mode === "light" ? "dark" : "light")}>
        <img className="w-[80%] h-[80%] m-auto" src="../favicon.png" alt="Asera Logo" />
    </button>
  );
}