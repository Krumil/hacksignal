export interface HackathonCardProps {
    title: string;
    organizer: string;
    prizePool: number;
    duration: number;
    relevanceScore: number;
    tags: string[];

    // Optional extended fields provided by backend
    id?: string;
    description?: string;
    deadline?: string;
    registrationUrl?: string;
    website?: string;
    location?: string;
    sourceScore?: number;
    sourceFollowers?: number;
    sourceKeywords?: string[];
    lastUpdated?: string;
}

export interface HackathonDashboardProps {
    hackathons: HackathonCardProps[];
    isLoading?: boolean;
    error?: string;
    onRefresh?: () => void;
}

export interface GridPatternProps {
    width: number;
    height: number;
    x: string;
    y: string;
    squares?: number[][];
    className?: string;
}
