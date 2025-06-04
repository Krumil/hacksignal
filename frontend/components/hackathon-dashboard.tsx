"use client";
import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, Trophy, RefreshCw, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { HackathonCard } from "@/components/hackathon-card";
import { HackathonDashboardProps } from "@/types/hackathon";

export const HackathonDashboard = ({ hackathons, isLoading, error, onRefresh }: HackathonDashboardProps) => {
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
            hackathon.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            hackathon.organizer?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesPrize = hackathon.prizePool >= prizeRange[0] && hackathon.prizePool <= prizeRange[1];
        const matchesDuration = hackathon.duration >= durationRange[0] && hackathon.duration <= durationRange[1];
        const matchesTab =
            activeTab === "all" || hackathon.tags?.some((tag) => tag.toLowerCase().includes(activeTab.toLowerCase()));

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
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold">Hackathon Dashboard</h1>
                            <p className="text-muted-foreground">
                                Discover and join exciting hackathons from around the world
                            </p>
                        </div>
                        <Button onClick={onRefresh} disabled={isLoading} variant="outline" size="sm">
                            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
                            Refresh Data
                        </Button>
                    </div>
                </div>

                {error && (
                    <Card className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950">
                        <CardContent className="pt-6">
                            <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
                                <AlertCircle className="h-4 w-4" />
                                <p className="text-sm">{error}</p>
                            </div>
                        </CardContent>
                    </Card>
                )}

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
                                    {isLoading ? (
                                        <div className="space-y-3">
                                            {[1, 2, 3].map((i) => (
                                                <div key={i} className="animate-pulse flex items-center space-x-3">
                                                    <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                                                    <div className="flex-1 space-y-1">
                                                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                                                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : hackathons.length > 0 ? (
                                        hackathons
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
                                            ))
                                    ) : (
                                        <p className="text-sm text-muted-foreground">No hackathons available</p>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="lg:col-span-2">
                        {isLoading ? (
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {[1, 2, 3, 4].map((i) => (
                                    <div key={i} className="animate-pulse">
                                        <Card className="h-64">
                                            <CardHeader>
                                                <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                                                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="space-y-3">
                                                    <div className="h-4 bg-gray-200 rounded"></div>
                                                    <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    </div>
                                ))}
                            </div>
                        ) : (
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
                        )}
                        <div className="mt-4 text-sm text-muted-foreground">
                            Showing {filteredHackathons.length} of {hackathons.length} hackathons
                            {isLoading && " (Loading...)"}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
