"use client";
import React, { useState, useEffect } from "react";
import { HackathonDashboard } from "@/components/hackathon-dashboard";
import { HackathonCardProps } from "@/types/hackathon";

export default function Home() {
    const [hackathons, setHackathons] = useState<HackathonCardProps[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | undefined>(undefined);

    const fetchHackathons = async () => {
        setIsLoading(true);
        setError(undefined);

        try {
            const response = await fetch("/api/hackathons");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to fetch hackathons");
            }

            let hackathonData: HackathonCardProps[] = [];

            if (data.source === "backend_api" && data.hackathons) {
                if (Array.isArray(data.hackathons)) {
                    // Backend now provides pre-transformed hackathon data
                    // Just map to ensure it matches our interface
                    hackathonData = data.hackathons.map((hackathon: any) => ({
                        title: hackathon.title || "Innovation Challenge",
                        organizer: hackathon.organizer || "TechCorp",
                        prizePool: hackathon.prizePool || 10000,
                        duration: hackathon.duration || 7,
                        relevanceScore: hackathon.relevanceScore || 50,
                        tags: hackathon.tags || ["Innovation", "Technology"],
                        registrationUrl: hackathon.registrationUrl,
                        website: hackathon.website,
                        id: hackathon.id,
                        description: hackathon.description,
                        deadline: hackathon.deadline,
                        location: hackathon.location,
                    }));

                    // Debug log to check URLs
                    console.log(
                        "🔗 Sample hackathon URLs:",
                        hackathonData.slice(0, 2).map((h) => ({
                            title: h.title,
                            registrationUrl: h.registrationUrl,
                            website: h.website,
                        }))
                    );
                } else {
                    console.error("❌ Backend hackathons is not an array!");
                    hackathonData = [];
                }
            } else if (data.source === "fallback_data") {
                hackathonData = data.hackathons || [];
                setError("Using fallback data - backend not available");
            } else if (data.hackathons) {
                hackathonData = data.hackathons || [];
            } else {
                console.error("❌ No hackathons data found in response!");
                hackathonData = [];
            }

            setHackathons(hackathonData);
        } catch (err) {
            console.error("❌ Failed to fetch hackathons:", err);
            setError(err instanceof Error ? err.message : "Failed to fetch hackathons");

            // Emergency fallback data
            const emergencyData = [
                {
                    title: "AI Innovation Challenge",
                    organizer: "TechCorp",
                    prizePool: 25000,
                    duration: 14,
                    relevanceScore: 95,
                    tags: ["AI", "Machine Learning", "Innovation"],
                },
                {
                    title: "Blockchain Builders Hackathon",
                    organizer: "CryptoFoundation",
                    prizePool: 15000,
                    duration: 7,
                    relevanceScore: 88,
                    tags: ["Crypto", "Blockchain", "Web3"],
                },
            ];
            setHackathons(emergencyData);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRefresh = async () => {
        await fetchHackathons();
    };

    useEffect(() => {
        fetchHackathons();
    }, []);

    console.log(
        "🎨 Rendering Home component - hackathons count:",
        hackathons.length,
        "isLoading:",
        isLoading,
        "error:",
        error
    );

    console.log("🎨 Current hackathons state:", hackathons);

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-muted/20 to-background dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
            <HackathonDashboard hackathons={hackathons} isLoading={isLoading} error={error} onRefresh={handleRefresh} />
        </div>
    );
}
