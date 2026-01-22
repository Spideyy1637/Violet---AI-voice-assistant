import * as LucideIcons from 'lucide-react';
import { LucideProps } from 'lucide-react';

interface IconProps extends LucideProps {
    name: keyof typeof LucideIcons;
}

const Icon = ({ name, ...props }: IconProps) => {
    const LucideIcon = LucideIcons[name] as React.ComponentType<LucideProps>;

    if (!LucideIcon) {
        console.warn(`Icon "${name}" not found in lucide-react`);
        return null;
    }

    return <LucideIcon {...props} />;
};

export default Icon;
