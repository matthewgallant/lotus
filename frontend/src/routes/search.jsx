import { useForm } from "react-hook-form"
import Button from "react-bootstrap/Button"
import Form from "react-bootstrap/Form"
import InputGroup from "react-bootstrap/InputGroup"
import '../assets/css/icons.css'

export default function SearchPage() {
    document.title = "Lotus :: Search";

    const { register, handleSubmit } = useForm()

    const onSubmit = (data) => {
        const options = {
            method: "POST",
            mode: "no-cors",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data)
        }
        
        fetch("/api/search", options)
            .then(res => res.json())
            .then(data => {
                console.log(data)
            })
    }

    return (
        <>
            <h1 className="my-3">Search</h1>
            <Form onSubmit={handleSubmit(onSubmit)}>
                <InputGroup className="mb-3">
                    <InputGroup.Text id="nameInput">Name</InputGroup.Text>
                    <Form.Control
                        placeholder="Enter a name..."
                        aria-label="Name"
                        aria-describedby="nameInput"
                        {...register("name")}
                    />
                </InputGroup>
                <InputGroup className="mb-3">
                    <InputGroup.Text id="typeDatalist">Type</InputGroup.Text>
                    <Form.Control
                        placeholder="Type to search..."
                        aria-label="Card type"
                        aria-describedby="typeDatalist"
                        {...register("type")}
                    />
                </InputGroup>
                <InputGroup className="mb-3">
                    <InputGroup.Text id="textInput">Text</InputGroup.Text>
                    <Form.Control
                        placeholder="Enter some card text..."
                        aria-label="Card text"
                        aria-describedby="textInput"
                        {...register("text")}
                    />
                </InputGroup>
                <InputGroup className="mb-3">
                    <InputGroup.Text id="setDatalist">Set</InputGroup.Text>
                    <Form.Control
                        placeholder="Type to search..."
                        aria-label="Set"
                        aria-describedby="setDatalist"
                        {...register("set")}
                    />
                </InputGroup>
                <InputGroup className="mb-3">
                    <InputGroup.Text id="raritySelect">Rarity</InputGroup.Text>
                    <Form.Select aria-label="Rarity" aria-describedby="raritySelect" {...register("rarity")}>
                        <option value="">Choose a rarity...</option>
                        <option value="mythic">Mythic</option>
                        <option value="rare">Rare</option>
                        <option value="uncommon">Uncommon</option>
                        <option value="common">Common</option>
                    </Form.Select>
                </InputGroup>
                <Form.Group className="mb-3">
                    <Form.Check type="checkbox" id="whiteColor">
                        <Form.Check.Input type="checkbox" {...register("white")} />
                        <Form.Check.Label className="color-icon color-icon-white">White</Form.Check.Label>
                    </Form.Check>
                    <Form.Check type="checkbox" id="blueColor">
                        <Form.Check.Input type="checkbox" {...register("blue")} />
                        <Form.Check.Label className="color-icon color-icon-blue">Blue</Form.Check.Label>
                    </Form.Check>
                    <Form.Check type="checkbox" id="blackColor">
                        <Form.Check.Input type="checkbox" {...register("black")} />
                        <Form.Check.Label className="color-icon color-icon-black">Black</Form.Check.Label>
                    </Form.Check>
                    <Form.Check type="checkbox" id="redColor">
                        <Form.Check.Input type="checkbox" {...register("red")} />
                        <Form.Check.Label className="color-icon color-icon-red">Red</Form.Check.Label>
                    </Form.Check>
                    <Form.Check type="checkbox" id="greenColor">
                        <Form.Check.Input type="checkbox" {...register("green")} />
                        <Form.Check.Label className="color-icon color-icon-green">Green</Form.Check.Label>
                    </Form.Check>
                    <Form.Check type="checkbox" id="uncoloredColor">
                        <Form.Check.Input type="checkbox" {...register("uncolored")} />
                        <Form.Check.Label className="color-icon color-icon-colorless">Uncolored</Form.Check.Label>
                    </Form.Check>
                </Form.Group>
                <Button variant="primary" type="submit">
                    Search
                </Button>
            </Form>
        </>
    );
}
