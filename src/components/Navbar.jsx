import { Link } from 'react-router-dom';
import Popout from "./Popout";

export default function Navbar({ user }) {

  let loggedin;

  if (user) {
    if (user.user_metadata.display_name){
      loggedin = (<div className='flex flex-row gap-4 items-center'>
        <p className='white-text'>Welcome, {user.user_metadata.display_name}</p>
        <Popout user={user} />
      </div>)
    }
    else {
      loggedin = (<div className='flex flex-row gap-4 items-center'>
        <p className='white-text'>{user.email}</p>
        <Popout user={user} />
      </div>)
    }
  }
  
  return (
    <div className='flex justify-between items-center gap-5 p-3 h-20 border-b-4 bg-main border-[#3AB3FF]'>

      <Link to="/">
        <img className="logo" src="../../public/QUORRA.png" alt="QUORRA Logo" width="180" />
      </Link>

        {loggedin}
    </div>
  );
}
