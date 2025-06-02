"use client";
import React, { useState, useId, useEffect } from "react";
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Clock, DollarSign, Search, Trophy, Users } from "lucide-react";

// Types
interface HackathonCardProps {
    title: string;
    organizer: string;
    prizePool: number;
    duration: number;
    relevanceScore: number;
    tags: string[];
}

interface HackathonDashboardProps {
    hackathons: HackathonCardProps[];
}

interface GridPatternProps {
    width: number;
    height: number;
    x: string;
    y: string;
    squares?: number[][];
    className?: string;
}

// Grid Pattern Component
const GridPattern = ({ width, height, x, y, squares, className, ...props }: GridPatternProps) => {
    const patternId = useId();

    return (
        <svg aria-hidden="true" className={className} {...props}>
            <defs>
                <pattern id={patternId} width={width} height={height} patternUnits="userSpaceOnUse" x={x} y={y}>
                    <path d={`M.5 ${height}V.5H${width}`} fill="none" />
                </pattern>
            </defs>
            <rect width="100%" height="100%" strokeWidth={0} fill={`url(#${patternId})`} />
            {squares && (
                <svg x={x} y={y} className="overflow-visible">
                    {squares.map(([x, y]: number[], i: number) => (
                        <rect
                            strokeWidth="0"
                            key={`${x}-${y}-${i}`}
                            width={width + 1}
                            height={height + 1}
                            x={x * width}
                            y={y * height}
                        />
                    ))}
                </svg>
            )}
        </svg>
    );
};

// Grid Component
const Grid = ({ pattern, size }: { pattern?: number[][]; size?: number }) => {
    const [clientPattern, setClientPattern] = useState<number[][] | null>(null);

    useEffect(() => {
        if (!pattern) {
            const randomPattern = [
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
                [Math.floor(Math.random() * 4) + 7, Math.floor(Math.random() * 6) + 1],
            ];
            setClientPattern(randomPattern);
        }
    }, [pattern]);

    const p = pattern ?? clientPattern ?? [];

    return (
        <div className="pointer-events-none absolute left-1/2 top-0 -ml-20 -mt-2 h-full w-full [mask-image:linear-gradient(white,transparent)]">
            <div className="absolute inset-0 bg-gradient-to-r [mask-image:radial-gradient(farthest-side_at_top,white,transparent)] dark:from-zinc-900/30 from-zinc-100/30 to-zinc-300/30 dark:to-zinc-900/30 opacity-100">
                <GridPattern
                    width={size ?? 20}
                    height={size ?? 20}
                    x="-12"
                    y="4"
                    squares={p}
                    className="absolute inset-0 h-full w-full mix-blend-overlay dark:fill-white/10 dark:stroke-white/10 stroke-black/10 fill-black/10"
                />
            </div>
        </div>
    );
};

// Hackathon Card Component
const HackathonCard = ({ title, organizer, prizePool, duration, relevanceScore, tags }: HackathonCardProps) => {
    return (
        <Card className="group relative overflow-hidden backdrop-blur-sm border border-border/50 bg-gradient-to-r from-purple-200 via-violet-400 to-indigo-600 p-px">
            <div className="absolute inset-0 bg-background/90 rounded-lg" />
            <Grid size={20} />

            <CardHeader className="relative z-10">
                <div className="flex justify-between items-start">
                    <div>
                        <h3 className="text-xl font-bold">{title}</h3>
                        <div className="flex items-center text-muted-foreground mt-1">
                            <Users className="h-4 w-4 mr-1" />
                            <span className="text-sm">{organizer}</span>
                        </div>
                    </div>
                    <Badge className="bg-background/50 backdrop-blur-sm">{relevanceScore}% Match</Badge>
                </div>
            </CardHeader>

            <CardContent className="relative z-10 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center">
                        <DollarSign className="h-4 w-4 mr-2 text-green-500" />
                        <div>
                            <p className="text-sm text-muted-foreground">Prize Pool</p>
                            <p className="font-medium">${prizePool.toLocaleString()}</p>
                        </div>
                    </div>
                    <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-2 text-blue-500" />
                        <div>
                            <p className="text-sm text-muted-foreground">Duration</p>
                            <p className="font-medium">{duration} days</p>
                        </div>
                    </div>
                </div>
            </CardContent>

            <CardFooter className="relative z-10 flex flex-wrap gap-2">
                {tags.map((tag, index) => (
                    <Badge key={index} className="bg-background/50 backdrop-blur-sm">
                        {tag}
                    </Badge>
                ))}
            </CardFooter>
        </Card>
    );
};

// Main Dashboard Component
const HackathonDashboard = ({ hackathons }: HackathonDashboardProps) => {
    const [searchQuery, setSearchQuery] = useState("");
    const [prizeRange, setPrizeRange] = useState([0, 50000]);
    const [durationRange, setDurationRange] = useState([1, 30]);
    const [activeTab, setActiveTab] = useState("all");
    const [isClient, setIsClient] = useState(false);

    useEffect(() => {
        setIsClient(true);
    }, []);

    // Filter hackathons based on search, prize range, and duration
    const filteredHackathons = hackathons.filter((hackathon) => {
        const matchesSearch =
            hackathon.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            hackathon.organizer.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesPrize = hackathon.prizePool >= prizeRange[0] && hackathon.prizePool <= prizeRange[1];
        const matchesDuration = hackathon.duration >= durationRange[0] && hackathon.duration <= durationRange[1];
        const matchesTab = activeTab === "all" || hackathon.tags.includes(activeTab);

        return matchesSearch && matchesPrize && matchesDuration && matchesTab;
    });

    // Show loading state during hydration to prevent mismatch
    if (!isClient) {
        return (
            <div className="container mx-auto py-8 px-4">
                <div className="flex flex-col space-y-6">
                    <div className="flex flex-col space-y-2">
                        <h1 className="text-3xl font-bold">Hackathon Dashboard</h1>
                        <p className="text-muted-foreground">
                            Discover and join exciting hackathons from around the world
                        </p>
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-1 space-y-6">
                            <Card className="backdrop-blur-sm bg-background/80 border-border/50">
                                <CardHeader>
                                    <h3 className="text-lg font-medium">Filters</h3>
                                </CardHeader>
                                <CardContent>
                                    <div className="animate-pulse space-y-4">
                                        <div className="h-4 bg-gray-200 rounded"></div>
                                        <div className="h-4 bg-gray-200 rounded"></div>
                                        <div className="h-4 bg-gray-200 rounded"></div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                        <div className="lg:col-span-2">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <div className="animate-pulse">
                                    <div className="h-32 bg-gray-200 rounded"></div>
                                </div>
                                <div className="animate-pulse">
                                    <div className="h-32 bg-gray-200 rounded"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto py-8 px-4">
            <div className="flex flex-col space-y-6">
                <div className="flex flex-col space-y-2">
                    <h1 className="text-3xl font-bold">Hackathon Dashboard</h1>
                    <p className="text-muted-foreground">Discover and join exciting hackathons from around the world</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-1 space-y-6">
                        <Card className="backdrop-blur-sm bg-background/80 border-border/50">
                            <CardHeader>
                                <h3 className="text-lg font-medium">Filters</h3>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <label className="text-sm font-medium">Search</label>
                                    </div>
                                    <div className="relative">
                                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                        <Input
                                            placeholder="Search hackathons..."
                                            className="pl-8"
                                            value={searchQuery}
                                            onChange={(e) => setSearchQuery(e.target.value)}
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <label className="text-sm font-medium">Prize Pool</label>
                                        <span className="text-xs text-muted-foreground">
                                            ${prizeRange[0].toLocaleString()} - ${prizeRange[1].toLocaleString()}
                                        </span>
                                    </div>
                                    <Slider
                                        defaultValue={prizeRange}
                                        min={0}
                                        max={50000}
                                        step={1000}
                                        onValueChange={setPrizeRange}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <label className="text-sm font-medium">Duration (days)</label>
                                        <span className="text-xs text-muted-foreground">
                                            {durationRange[0]} - {durationRange[1]} days
                                        </span>
                                    </div>
                                    <Slider
                                        defaultValue={durationRange}
                                        min={1}
                                        max={30}
                                        step={1}
                                        onValueChange={setDurationRange}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Categories</label>
                                    <Tabs defaultValue="all" onValueChange={setActiveTab}>
                                        <TabsList className="grid grid-cols-3 w-full">
                                            <TabsTrigger value="all">All</TabsTrigger>
                                            <TabsTrigger value="AI">AI</TabsTrigger>
                                            <TabsTrigger value="Crypto">Crypto</TabsTrigger>
                                        </TabsList>
                                    </Tabs>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="backdrop-blur-sm bg-background/80 border-border/50">
                            <CardHeader>
                                <h3 className="text-lg font-medium">Top Hackathons</h3>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {hackathons
                                        .sort((a, b) => b.relevanceScore - a.relevanceScore)
                                        .slice(0, 3)
                                        .map((hackathon, index) => (
                                            <div key={index} className="flex items-center space-x-3">
                                                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary">
                                                    <Trophy className="h-4 w-4" />
                                                </div>
                                                <div>
                                                    <p className="text-sm font-medium">{hackathon.title}</p>
                                                    <p className="text-xs text-muted-foreground">
                                                        {hackathon.organizer}
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="lg:col-span-2">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {filteredHackathons.length > 0 ? (
                                filteredHackathons.map((hackathon, index) => (
                                    <HackathonCard key={index} {...hackathon} />
                                ))
                            ) : (
                                <div className="lg:col-span-2 flex flex-col items-center justify-center p-12 text-center">
                                    <Search className="h-12 w-12 text-muted-foreground mb-4" />
                                    <h3 className="text-lg font-medium">No hackathons found</h3>
                                    <p className="text-muted-foreground">
                                        Try adjusting your filters to find more hackathons
                                    </p>
                                </div>
                            )}
                        </div>
                        <div className="mt-4 text-sm text-muted-foreground">
                            Showing {filteredHackathons.length} of {hackathons.length} hackathons
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Example usage with sample data
export default function Home() {
    const sampleHackathons: HackathonCardProps[] = [
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
        {
            title: "Global AI Summit Hackathon",
            organizer: "AI Alliance",
            prizePool: 30000,
            duration: 21,
            relevanceScore: 92,
            tags: ["AI", "Data Science", "NLP"],
        },
        {
            title: "DeFi Development Challenge",
            organizer: "Ethereum Foundation",
            prizePool: 20000,
            duration: 10,
            relevanceScore: 85,
            tags: ["Crypto", "DeFi", "Smart Contracts"],
        },
        {
            title: "Computer Vision Hackathon",
            organizer: "Vision Tech",
            prizePool: 12000,
            duration: 5,
            relevanceScore: 78,
            tags: ["AI", "Computer Vision", "Deep Learning"],
        },
        {
            title: "NFT Creation Challenge",
            organizer: "Digital Art Collective",
            prizePool: 8000,
            duration: 3,
            relevanceScore: 72,
            tags: ["Crypto", "NFT", "Digital Art"],
        },
    ];

    return <HackathonDashboard hackathons={sampleHackathons} />;
}
