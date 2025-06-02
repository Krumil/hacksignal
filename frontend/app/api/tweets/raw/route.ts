import { NextResponse } from "next/server";
import { BackendAPI } from "@/lib/backend-api";

export async function GET() {
    try {
        const tweets = await BackendAPI.getRawTweets();
        return NextResponse.json(tweets);
    } catch (error) {
        console.error("Failed to fetch raw tweets:", error);
        return NextResponse.json({ error: "Failed to fetch raw tweets from backend" }, { status: 500 });
    }
}
