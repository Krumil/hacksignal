import { NextResponse } from "next/server";
import { BackendAPI } from "@/lib/backend-api";

export async function POST() {
    try {
        const result = await BackendAPI.runPipeline();
        return NextResponse.json(result);
    } catch (error) {
        console.error("Failed to run pipeline:", error);
        return NextResponse.json({ error: "Failed to trigger pipeline" }, { status: 500 });
    }
}
