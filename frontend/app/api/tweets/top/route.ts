import { NextRequest, NextResponse } from "next/server";
import { BackendAPI } from "@/lib/backend-api";

export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);
        const limit = parseInt(searchParams.get("limit") || "20");

        const tweets = await BackendAPI.getTopTweets(limit);
        return NextResponse.json(tweets);
    } catch (error) {
        console.error("Failed to fetch top tweets:", error);
        return NextResponse.json({ error: "Failed to fetch top tweets from backend" }, { status: 500 });
    }
}
