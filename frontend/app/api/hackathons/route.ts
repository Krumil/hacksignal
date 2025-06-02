import { NextResponse } from "next/server";
import { BackendAPI } from "@/lib/backend-api";

// This would connect to the Python backend in a real implementation
export async function GET() {
    try {
        // Get top tweets from the backend (these represent potential hackathons)
        const tweets = await BackendAPI.getTopTweets(20);

        // Transform tweets data into hackathon format if needed
        // For now, returning the tweets as they are from the backend
        return NextResponse.json({
            hackathons: tweets,
            source: "backend_api",
        });
    } catch (error) {
        console.error("Failed to fetch hackathons from backend:", error);

        // Fallback to mock data if backend is unavailable
        const fallbackHackathons = [
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

        return NextResponse.json({
            hackathons: fallbackHackathons,
            source: "fallback_data",
            error: "Backend unavailable",
        });
    }
}

// Future endpoint to connect to Python backend
export async function POST() {
    try {
        // Trigger the backend pipeline to refresh data
        const result = await BackendAPI.runPipeline();
        return NextResponse.json(result);
    } catch (error) {
        console.error("Failed to trigger pipeline:", error);
        return NextResponse.json({ error: "Failed to trigger pipeline refresh" }, { status: 500 });
    }
}
