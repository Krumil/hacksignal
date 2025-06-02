import { NextResponse } from "next/server";
import { BackendAPI } from "@/lib/backend-api";

export async function POST() {
    try {
        const result = await BackendAPI.quickTest();
        return NextResponse.json(result);
    } catch (error) {
        console.error("Failed to run quick test:", error);
        return NextResponse.json({ error: "Failed to run quick test" }, { status: 500 });
    }
}
