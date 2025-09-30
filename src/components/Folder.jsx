import { useState } from "react";

export default function Folder({ folder }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="">
      <div
        className="cursor-pointer select-none flex items-center p-1 text-sm mb-2 rounded bg-gray-700 hover:bg-gray-600"
        onClick={() => setOpen(!open)}>
        {/* May want to add folder icons */}
        <p className="ml-2">{folder.name}</p>
      </div>
    
    {/* Need to add something in case text is too large */}
      {open && folder.children && (
        <div className="ml-5">
          {folder.children.map((child) => (
            <Folder key={child.id} folder={child} />
          ))}
        </div>
      )}
    </div>
  );
}
