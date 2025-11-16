import { useState } from "react";
import { Link } from "react-router-dom";

export default function Profile() {


  return (
    <div className="w-full h-full">
        <div className="flex flex-col m-10 p-10 rounded white-text shadow bg-diff">
            <h1 className="text-center relative text-2xl">Profile Settings</h1>
            <div className="flex flex-col gap-4 mt-10">
                <div className="flex flex-row justify-between">
                    <p className="text-xl">Display Name:</p>
                    <p>Placeholder</p>
                </div>
                <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>

                <div className="flex flex-row justify-between">
                    <p className="text-xl">Email:</p>
                    <p>Placeholder</p>
                </div>
                <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>
                <div className="flex flex-row justify-between">
                    <p className="text-xl">Account Created:</p>
                    <p>Placeholder</p>
                </div>
                <div className="bg-diff border-t-2 border-[#3AB3FF] mb-5"></div>


                <button className="bg-[#3AB3FF] m-auto p-2 rounded text-lg text-white">Change Password</button>

            </div>
        </div>
    </div>
  );
}
