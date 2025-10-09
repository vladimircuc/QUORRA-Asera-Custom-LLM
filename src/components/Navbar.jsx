export default function Navbar() {
  return (
      <div className='flex justify-between items-center gap-5 p-3 h-20 border-b-4 bg-main border-[#3AB3FF]'>
        <img className="logo" src="../../public/QUORRA.png" alt="QUORRA Logo" width="180"/>
        <div className='w-10 h-10 bg-sky-500 rounded-4xl mr-4'></div>
      </div>
  );
}