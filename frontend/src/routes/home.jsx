import { useState, useEffect } from 'react'
import Image from 'react-bootstrap/Image';
import logo from '../assets/images/logo.png';

export default function HomePage() {
    document.title = "Lotus :: Home";

    const [total, setTotal] = useState(0)

    useEffect(() => {
        fetch('/api/home')
            .then(res => res.json())
            .then(data => {
                if (data?.total) {
                    setTotal(data.total)
                }
            })
    }, [])

    return (
        <div className="mt-5 d-sm-flex justify-content-center align-items-center text-center gap-5">
            <div>
                <Image src={logo} style={{ height: 150 }} fluid />
            </div>
            <div className="mt-4 mt-sm-0">
                <h1>Welcome to Lotus!</h1>
                <p>You have {total} cards in your collection</p>
                <div className="d-flex justify-content-center gap-2">
                    <a href="/search" className="btn btn-primary">Search Collection</a>
                    <a href="/decks" className="btn btn-secondary">View Decks</a>
                </div>
            </div>
        </div>
    );
}