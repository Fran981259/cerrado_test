import {
  ChartNoAxesColumnIncreasing,
  CircleDot,
  Clapperboard,
  CloudSun,
  Goal,
  GraduationCap,
  Hospital,
  Landmark,
  Laptop,
  Microscope,
  Newspaper,
  Palette,
  ShieldCheck,
  Wheat,
  type LucideIcon,
} from "lucide-react";

const ICONS: Record<string, LucideIcon> = {
  laptop: Laptop,
  football: Goal,
  landmark: Landmark,
  chart: ChartNoAxesColumnIncreasing,
  hospital: Hospital,
  shield: ShieldCheck,
  microscope: Microscope,
  clapperboard: Clapperboard,
  wheat: Wheat,
  graduation: GraduationCap,
  palette: Palette,
  cloud: CloudSun,
  newspaper: Newspaper,
};

/** Renders one icon from the centralized editorial icon vocabulary. */
export function Icon({ name, className = "" }: { name: string; className?: string }) {
  const Component = ICONS[name] || CircleDot;
  return <Component aria-hidden="true" className={className} strokeWidth={2} />;
}
