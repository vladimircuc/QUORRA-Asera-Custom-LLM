import { Link } from 'react-router-dom';
import Popout from "./Popout";

export default function Navbar({ userEmail }) {
  return (
    <div className='flex justify-between items-center gap-5 p-3 h-20 border-b-4 bg-main border-[#3AB3FF]'>
      <Link to="/">
        <img className="logo" src="../../public/QUORRA.png" alt="QUORRA Logo" width="180" />
      </Link>

      
      <div className='flex flex-row gap-3 items-center'>
        {userEmail ? (
          <Popout userEmail={userEmail} />
        ) : (
          <span className="white-text"> </span>
        )}
      </div>
    </div>
  );
}
