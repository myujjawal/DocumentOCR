import React, { useEffect } from "react";
import axios from "axios";
const GetData = () => {
  const [data, setData] = React.useState([]);
  useEffect(() => {
    async function fetchData() {
      try {
        const res = await axios.get("http://127.0.0.1:8000/api/aadhar/");
        // console.log(res.data);
        setData(res.data);
      } catch (error) {
        console.log(error);
      }
    }
    fetchData();
  }, []);
  return (
    <div>
      {data.map((item, ind) => (
        <div key={ind}>
          <div>{item.name}</div>
          <div>{item.aadhaar_number}</div>
        </div>
      ))}
    </div>
  );
};

export default GetData;
