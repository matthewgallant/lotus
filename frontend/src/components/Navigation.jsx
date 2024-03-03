import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';

import logo from '../assets/images/logo.png';

export default function Navigation() {
    return (
        <Navbar collapseOnSelect expand="lg" className="bg-primary" data-bs-theme="dark">
            <Container>
                <Navbar.Brand href="/">
                    <img
                        alt=""
                        src={logo}
                        width="30"
                        height="30"
                        className="d-inline-block align-top me-2"
                    />
                    Lotus
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="responsive-navbar-nav" />
                <Navbar.Collapse id="responsive-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link href="/search">Search</Nav.Link>
                        <Nav.Link href="/decks">Decks</Nav.Link>
                        <Nav.Link href="/cards/add">Add Cards</Nav.Link>
                        <Nav.Link href="/import">Import</Nav.Link>
                    </Nav>
                    <Form inline className='d-flex gap-2'>
                        <Form.Control type="text" placeholder="Search: &#8984; + /" />
                        <Button type="submit" variant="outline-light">Search</Button>
                    </Form>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
}