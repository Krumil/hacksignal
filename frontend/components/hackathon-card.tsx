import React, { useRef, useMemo } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, DollarSign, Users, Award, ExternalLink } from "lucide-react";
import { HackathonCardProps } from "@/types/hackathon";
import { cn } from "@/lib/utils";

// Hooks
interface Dimensions {
    width: number;
    height: number;
}

function useDimensions(ref: React.RefObject<HTMLElement | SVGElement | null>): Dimensions {
    const [dimensions, setDimensions] = React.useState<Dimensions>({ width: 0, height: 0 });

    React.useEffect(() => {
        let timeoutId: NodeJS.Timeout;

        const updateDimensions = () => {
            if (ref.current) {
                const { width, height } = ref.current.getBoundingClientRect();
                setDimensions({ width, height });
            }
        };

        const debouncedUpdateDimensions = () => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(updateDimensions, 250);
        };

        // Initial measurement
        updateDimensions();

        window.addEventListener("resize", debouncedUpdateDimensions);

        return () => {
            window.removeEventListener("resize", debouncedUpdateDimensions);
            clearTimeout(timeoutId);
        };
    }, [ref]);

    return dimensions;
}

// Animated Gradient Component
interface AnimatedGradientProps {
    colors: string[];
    speed?: number;
    blur?: "light" | "medium" | "heavy";
}

const randomInt = (min: number, max: number) => {
    return Math.floor(Math.random() * (max - min + 1)) + min;
};

const AnimatedGradient: React.FC<AnimatedGradientProps> = ({ colors, speed = 5, blur = "light" }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const dimensions = useDimensions(containerRef);

    const circleSize = useMemo(
        () => Math.max(dimensions.width, dimensions.height),
        [dimensions.width, dimensions.height]
    );

    const blurClass = blur === "light" ? "blur-2xl" : blur === "medium" ? "blur-3xl" : "blur-[100px]";

    return (
        <div ref={containerRef} className="absolute inset-0 overflow-hidden">
            <div className={cn(`absolute inset-0`, blurClass)}>
                {colors.map((color, index) => (
                    <svg
                        key={index}
                        className="absolute animate-background-gradient"
                        style={
                            {
                                top: `${Math.random() * 50}%`,
                                left: `${Math.random() * 50}%`,
                                "--background-gradient-speed": `${1 / speed}s`,
                                "--tx-1": Math.random() - 0.5,
                                "--ty-1": Math.random() - 0.5,
                                "--tx-2": Math.random() - 0.5,
                                "--ty-2": Math.random() - 0.5,
                                "--tx-3": Math.random() - 0.5,
                                "--ty-3": Math.random() - 0.5,
                                "--tx-4": Math.random() - 0.5,
                                "--ty-4": Math.random() - 0.5,
                            } as React.CSSProperties
                        }
                        width={circleSize * randomInt(0.5, 1.5)}
                        height={circleSize * randomInt(0.5, 1.5)}
                        viewBox="0 0 100 100"
                    >
                        <circle cx="50" cy="50" r="50" fill={color} className="opacity-30 dark:opacity-[0.15]" />
                    </svg>
                ))}
            </div>
        </div>
    );
};

export const HackathonCard = ({
    title,
    organizer,
    prizePool,
    duration,
    relevanceScore,
    tags,
    registrationUrl,
    website,
}: HackathonCardProps) => {
    // Generate colors based on tags
    const generateColors = (tags: string[]) => {
        const colorMap: { [key: string]: string[] } = {
            AI: ["#3B82F6", "#60A5FA", "#93C5FD"],
            Web3: ["#60A5FA", "#34D399", "#93C5FD"],
            Blockchain: ["#34D399", "#A78BFA", "#60A5FA"],
            Crypto: ["#EC4899", "#F472B6", "#3B82F6"],
            Innovation: ["#F59E0B", "#A78BFA", "#FCD34D"],
            Technology: ["#8B5CF6", "#EC4899", "#6366F1"],
        };

        for (const tag of tags) {
            if (colorMap[tag]) return colorMap[tag];
        }
        return ["#3B82F6", "#A78BFA", "#60A5FA"]; // Default colors
    };

    const colors = generateColors(tags);

    // Determine the best URL to use for the link
    const linkUrl = registrationUrl || website || "#";
    const hasValidLink = linkUrl !== "#";

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1,
                delayChildren: 0.2,
            },
        },
    };

    const item = {
        hidden: { opacity: 0, y: 10 },
        show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
    };

    const handleLinkClick = () => {
        if (hasValidLink) {
            window.open(linkUrl, "_blank", "noopener,noreferrer");
        }
    };

    return (
        <motion.div
            className="relative h-full"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            whileHover={{ y: -5 }}
        >
            <Card className="h-full overflow-hidden border border-border/40 bg-background/80 backdrop-blur-md relative">
                <div className="absolute inset-0 opacity-50">
                    <AnimatedGradient colors={colors} speed={0.05} blur="medium" />
                </div>

                <motion.div
                    className="relative z-10 p-5 flex flex-col h-full"
                    variants={container}
                    initial="hidden"
                    animate="show"
                >
                    <motion.div variants={item} className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-bold text-foreground">{title}</h3>
                        <Badge variant="outline" className="bg-background/50 backdrop-blur-sm">
                            {relevanceScore}% Match
                        </Badge>
                    </motion.div>

                    <motion.div variants={item} className="grid grid-cols-2 gap-3 mb-4">
                        <div className="flex items-center text-sm text-foreground/80">
                            <DollarSign className="h-4 w-4 mr-2 text-green-500" />
                            <div>
                                <p className="text-xs text-muted-foreground">Prize Pool</p>
                                <p className="font-medium">${prizePool.toLocaleString()}</p>
                            </div>
                        </div>
                        <div className="flex items-center text-sm text-foreground/80">
                            <Clock className="h-4 w-4 mr-2 text-blue-500" />
                            <div>
                                <p className="text-xs text-muted-foreground">Duration</p>
                                <p className="font-medium">{duration} days</p>
                            </div>
                        </div>
                        <div className="flex items-center text-sm text-foreground/80 col-span-2">
                            <Users className="h-4 w-4 mr-2 text-primary" />
                            <span>{organizer}</span>
                        </div>
                    </motion.div>

                    <motion.div variants={item} className="flex flex-wrap gap-2 mt-auto pt-3">
                        {tags.map((tag, index) => (
                            <Badge key={index} variant="secondary" className="bg-primary/10 text-primary">
                                {tag}
                            </Badge>
                        ))}
                    </motion.div>

                    <motion.div variants={item} className="mt-4 pt-3 border-t border-border/50 flex justify-end">
                        <motion.button
                            className={`text-sm font-medium flex items-center ${
                                hasValidLink
                                    ? "text-primary hover:text-primary/80 cursor-pointer"
                                    : "text-muted-foreground cursor-not-allowed"
                            }`}
                            whileHover={hasValidLink ? { x: 3 } : {}}
                            onClick={handleLinkClick}
                            disabled={!hasValidLink}
                        >
                            {hasValidLink ? "View Details" : "Details Unavailable"}
                            <ExternalLink className="h-3 w-3 ml-1" />
                        </motion.button>
                    </motion.div>
                </motion.div>
            </Card>
        </motion.div>
    );
};
