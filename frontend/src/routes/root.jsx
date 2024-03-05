import { Outlet } from "react-router-dom"
import Container from 'react-bootstrap/Container'
import Navigation from '../components/Navigation'

export default function Root() {
    return (
        <div className='d-flex flex-column'>
            <Navigation />
            <div className="flex-grow-1 pt-2">
                <Container>
                    <Outlet />
                </Container>
            </div>
        </div>
    );
}