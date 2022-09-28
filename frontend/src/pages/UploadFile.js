import { useState } from "react";
import axios from "axios";

const UploadFile = () => {
  const [file, setFile] = useState({
    title: "",
    content: "AadharFront",
    image: null,
  });
  const [isSelected, setIsSelected] = useState(false);
  const [response, setResponse] = useState(null);
  // const [filename, setFilename] = useState("Choose File");

  const onChange = (e) => {
    setFile({
      ...file,
      image: e.target.files[0],
    });
    // setFilename(e.target.files[0].name);
    setIsSelected(true);
  };
  const handleChange = (e) => {
    setFile({
      ...file,
      [e.target.name]: e.target.value,
    });
  };
  const handleDropdown = (e) => {
    console.log(e.target.value);
    setFile({
      ...file,
      content: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // console.log("file jkhjkjkhjk");
    const formData = new FormData();

    formData.append("image", file.image, file.image.name);
    formData.append("title", file.title);
    formData.append("content", file.content);

    let url = "http://localhost:8000/api/aadharimg/";
    axios
      .post(url, formData, {
        headers: {
          "content-type": "multipart/form-data",
        },
      })
      .then((res) => {
        console.log(res.data, "42");
        setResponse(res.data);
      })
      .catch((err) => console.log(err));
  };

  return (
    <div className="p-20">
      <form
        className="flex flex-col items-center mt-10 space-y-6"
        onSubmit={handleSubmit}
      >
        <input
          type="text"
          placeholder="Title"
          id="title"
          name="title"
          value={file.title}
          onChange={handleChange}
          required
        />
        <select
          required
          id="content"
          name="content"
          value={file.content}
          onChange={handleDropdown}
        >
          <option value="AadharFront">AadharFront</option>
          <option value="AadharBack">AadharBack</option>
          <option value="PAN">PAN</option>
          <option value="Passport">Passport</option>
        </select>
        {/* <input
          type="text"
          placeholder="Content"
          id="content"
          name="content"
          value={file.content}
          onChange={handleChange}
          required
        /> */}

        <input type="file" onChange={onChange} required />
        {isSelected ? (
          <div>
            <p>Filename: {file.image.name}</p>
            <p>Filetype: {file.image.type}</p>
            <p>Size in bytes: {file.image.size}</p>
            <p>
              lastModifiedDate:{" "}
              {file.image.lastModifiedDate.toLocaleDateString()}
            </p>
          </div>
        ) : (
          <p className="mt-10">Select a file to show details</p>
        )}
        <input
          className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
          type="submit"
          value="Upload"
        />
        {/* <p>{filename}</p> */}
      </form>
      {response ? <p>{response["string"].content}</p> : null}
      <br />
      <br />
      {response ? (
        <div>
          <p>Name: {response["box"]?.Name}</p>
          <p>Gender: {response["box"]?.Gender}</p>
          <p>Date of Birth: {response["box"]?.Date}</p>
          <p>Aadhar Number: {response["box"]?.AadharNumber}</p>
        </div>
      ) : null}
    </div>
  );
};

export default UploadFile;
