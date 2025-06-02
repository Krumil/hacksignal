import { NextResponse } from "next/server";
import { BackendAPI } from "@/lib/backend-api";

export async function GET() {
    try {
        const healthStatus = await BackendAPI.health();
        return NextResponse.json(healthStatus);
    } catch (error) {
        console.error("Backend health check failed:", error);
        return NextResponse.json({ status: "error", error: "Backend unavailable" }, { status: 503 });
    }
}
