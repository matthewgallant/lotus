import { useRouteError } from "react-router-dom"
import Container from 'react-bootstrap/Container'

import Navigation from "./components/Navigation";

export default function ErrorPage() {
    const error = useRouteError();
    console.error(error);

    return (
        <div className='d-flex flex-column'>
            <Navigation />
            <div className="flex-grow-1 pt-2">
                <Container>
                    <h1>Oops!</h1>
                    <p>Sorry, an unexpected error has occurred.</p>
                    <p>
                        <i>{error.statusText || error.message}</i>
                    </p>
                </Container>
            </div>
        </div>
    );
}
