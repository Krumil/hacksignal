import { NextResponse } from "next/server";

// This would connect to the Python backend in a real implementation
export async function GET() {
    // Mock data - in production, this would fetch from the Python backend
    const hackathons = [
        {
            id: 1,
            title: "AI Innovation Challenge",
            organizer: "TechCorp",
            prizePool: 25000,
            duration: 14,
            relevanceScore: 95,
            tags: ["AI", "Machine Learning", "Innovation"],
            deadline: "2024-03-15T00:00:00Z",
            website: "https://example.com/ai-challenge",
        },
        {
            id: 2,
            title: "Blockchain Builders Hackathon",
            organizer: "CryptoFoundation",
            prizePool: 15000,
            duration: 7,
            relevanceScore: 88,
            tags: ["Crypto", "Blockchain", "Web3"],
            deadline: "2024-03-10T00:00:00Z",
            website: "https://example.com/blockchain-hack",
        },
    ];

    return NextResponse.json({ hackathons });
}

// Future endpoint to connect to Python backend
export async function POST() {
    // This would trigger a refresh from the Python backend
    // const result = await fetch('http://localhost:8000/api/refresh');
    return NextResponse.json({ message: "Refresh triggered" });
}
