import { NextRequest, NextResponse } from "next/server";
import { BackendAPI } from "@/lib/backend-api";

export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);
        const limit = parseInt(searchParams.get("limit") || "100");

        const tweets = await BackendAPI.getScoredTweets(limit);
        return NextResponse.json(tweets);
    } catch (error) {
        console.error("Failed to fetch scored tweets:", error);
        return NextResponse.json({ error: "Failed to fetch scored tweets from backend" }, { status: 500 });
    }
}
