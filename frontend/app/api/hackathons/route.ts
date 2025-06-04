import { NextResponse } from "next/server";
import { BackendAPI } from "@/lib/backend-api";

// This connects to the Python backend hackathons endpoint
export async function GET() {
    console.log("🔌 API Route: /api/hackathons GET called");
    try {
        console.log("🏆 Attempting to fetch hackathons from backend...");
        // Get pre-transformed hackathon data from the backend
        const hackathonsData = await BackendAPI.getTopHackathons(10);
        console.log("✅ Backend hackathons response received:", hackathonsData);

        // Return the hackathon data directly since it's already formatted
        const response = {
            hackathons: hackathonsData,
            source: "backend_api",
        };
        console.log("📤 Returning backend hackathon data:", response);
        return NextResponse.json(response);
    } catch (error) {
        console.error("❌ Failed to fetch hackathons from backend:", error);

        // Fallback to mock data if backend is unavailable
        const fallbackHackathons = [
            {
                id: "hack_fallback_1",
                title: "AI Innovation Challenge",
                organizer: "TechCorp",
                prizePool: 25000,
                duration: 14,
                relevanceScore: 95,
                tags: ["AI", "Machine Learning", "Innovation"],
                description:
                    "Build innovative solutions using artificial intelligence and machine learning. Compete with developers worldwide for $25,000 in total prizes. Great opportunity to showcase your skills and win significant rewards.",
                deadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
                registrationUrl: "https://example.com/ai-challenge",
                website: "https://example.com/ai-challenge",
                location: "Remote/Online",
            },
            {
                id: "hack_fallback_2",
                title: "Blockchain Builders Hackathon",
                organizer: "CryptoFoundation",
                prizePool: 15000,
                duration: 7,
                relevanceScore: 88,
                tags: ["Crypto", "Blockchain", "Web3"],
                description:
                    "Build innovative solutions using blockchain and distributed ledger technology. Compete with developers worldwide for $15,000 in total prizes. Perfect for learning, networking, and building your portfolio.",
                deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
                registrationUrl: "https://example.com/blockchain-hack",
                website: "https://example.com/blockchain-hack",
                location: "Remote/Online",
            },
        ];

        const fallbackResponse = {
            hackathons: fallbackHackathons,
            source: "fallback_data",
            error: "Backend unavailable",
        };
        console.log("🔄 Returning fallback hackathon data:", fallbackResponse);
        return NextResponse.json(fallbackResponse);
    }
}

// Trigger backend pipeline refresh
export async function POST() {
    console.log("🔌 API Route: /api/hackathons POST called");
    try {
        console.log("🚀 Triggering backend pipeline...");
        // Trigger the backend pipeline to refresh data
        const result = await BackendAPI.runPipeline();
        console.log("✅ Pipeline result:", result);
        return NextResponse.json(result);
    } catch (error) {
        console.error("❌ Failed to trigger pipeline:", error);
        return NextResponse.json({ error: "Failed to trigger pipeline refresh" }, { status: 500 });
    }
}
