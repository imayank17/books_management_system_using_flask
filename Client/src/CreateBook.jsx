import axios from 'axios'//core react library for building user interface
import React, {useState} from 'react'//for making requests to your backend server
import { useNavigate } from 'react-router-dom' // useNavigate use to navigate to different routes

const CreateBook = () => { // defined the functional component named createbook
    const [ values, setValues] = useState({
        publisher: "",
        name: "",
        date: '',
        cost: ''
    })
    const navigate = useNavigate() // navigate to the home page
    const handleSubmit = (e) => {    // event handler to handle form submission
        e.preventDefault()        // prevent default form submission
        axios.post('http://localhost:5001/create', values) // sends the post request to the server
            .then(res => navigate('/'))                        // on successful response user will be navigated to the home page 
            .catch(err => console.log(err))                    // logs error occur during request
    }
    return ( // div container contain flexbox classes to centring content
        <div className='d-flex align-items-center flex-column mt-3'> 
            <h2>Add a Book</h2>
            <form className='wt-50' onSubmit={handleSubmit}>
                <div className="mb-3 mt-3">
                    <label htmlFor="Publisher" className="form-label">Publisher</label>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Enter Publisher name"
                        name="publisher"
                        value={values.publisher}
                        onChange={(e) => setValues({ ...values, publisher: e.target.value })}
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="Book name" className="form-label">Book name:</label>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Enter Book name"
                        name="name"
                        value={values.name}
                        onChange={(e) => setValues({ ...values, name: e.target.value })}
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="Publish date" className="form-label">Publish Date:</label>
                    <input
                        type="date"
                        className="form-control"
                        name="date"
                        value={values.date}
                        onChange={(e) => setValues({ ...values, date: e.target.value })}
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="cost" className="form-label">cost:</label>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Enter cost"
                        name="cost"
                        value={values.cost}
                        onChange={(e) => setValues({ ...values, cost: e.target.value })}
                    />
                </div>
                <button type="submit" className="btn btn-primary">Submit</button>
            </form>
        </div>
    )
}

export default CreateBook