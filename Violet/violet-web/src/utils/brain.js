import dataset from '../data/dataset.json';

// Simple Math Evaluator (Safe)
const calculateMath = (expression) => {
    try {
        // Cleaning
        let cleanExpr = expression
            .toLowerCase()
            .replace(/what is/g, '')
            .replace(/calculate/g, '')
            .replace(/solve/g, '')
            .replace(/math/g, '')
            .replace(/plus/g, '+')
            .replace(/minus/g, '-')
            .replace(/times/g, '*')
            .replace(/multiplied by/g, '*')
            .replace(/divided by/g, '/')
            .replace(/over/g, '/')
            .replace(/x/g, '*')
            .trim();

        // Advanced replacements (consistent with backend logic)
        cleanExpr = cleanExpr
            .replace(/square root of/g, 'Math.sqrt')
            .replace(/sqrt/g, 'Math.sqrt')
            .replace(/pi/g, 'Math.PI')
            .replace(/\^/g, '**');

        // Check for allowed chars
        if (!/^[\d\+\-\*\/\(\)\.\sMath\.\w]+$/.test(cleanExpr)) return null;

        // Eval (using Function constructor for slightly better isolation than eval, though frontend is user's machine)
        // We only allow math!
        const result = new Function(`return ${cleanExpr}`)();

        if (isNaN(result)) return null;

        // Round to 4 decimal places if needed
        return Math.round(result * 10000) / 10000;
    } catch (e) {
        return null;
    }
};

const getLocalTime = () => {
    return new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
};

const getLocalDate = () => {
    return new Date().toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
};

// Emoji Personality
const addEmoji = (text) => {
    const t = text.toLowerCase();
    let emoji = '';

    if (t.includes('time')) emoji = ' ⏰';
    else if (t.includes('date') || t.includes('today')) emoji = ' 📅';
    else if (t.includes('math') || t.includes('answer') || t.includes('calculated')) emoji = ' 🔢';
    else if (t.includes('hello') || t.includes('hi ') || t.includes('hey')) emoji = ' 👋';
    else if (t.includes('violet')) emoji = ' 💜';
    else if (t.includes('weather')) emoji = ' 🌤️';
    else if (t.includes('sorry')) emoji = ' 😓';
    else if (t.includes('help')) emoji = ' 🤝';
    else if (t.includes('cool') || t.includes('nice')) emoji = ' 😎';

    return text + emoji;
}

// Fuzzy Search for Dataset
const searchDataset = (query) => {
    const q = query.toLowerCase().trim();

    // 1. Normal Conversation
    for (const item of dataset.normal_conversation) {
        if (item.question.toLowerCase() === q) {
            return item.answer;
        }
    }

    // 2. Real World Knowledge
    for (const item of dataset.real_world_knowledge) {
        if (item.question.toLowerCase() === q) {
            return item.answer;
        }
    }

    // 3. Simple Fuzzy Match (Startswith / Contains) - Can be improved
    const allItems = [...dataset.normal_conversation, ...dataset.real_world_knowledge];
    const match = allItems.find(item => item.question.toLowerCase().includes(q));

    if (match) return match.answer;

    return null;
};

export const processLocalCommand = (command) => {
    const lowerCmd = command.toLowerCase().trim();

    // 1. Time
    if (lowerCmd.includes('time') && (lowerCmd.includes('what') || lowerCmd.includes('current'))) {
        return addEmoji(`It's ${getLocalTime()}.`);
    }

    // 2. Date (exclude if asking about news)
    if ((lowerCmd.includes('date') || lowerCmd.includes('day is it') || lowerCmd.includes('today')) && !lowerCmd.includes('news') && !lowerCmd.includes('weather')) {
        return addEmoji(`Today is ${getLocalDate()}.`);
    }

    // 3. Math
    if (lowerCmd.match(/[\d]/) && (lowerCmd.includes('+') || lowerCmd.includes('-') || lowerCmd.includes('*') || lowerCmd.includes('/') || lowerCmd.includes('calculate') || lowerCmd.includes('solve'))) {
        const mathResult = calculateMath(command);
        if (mathResult !== null) return addEmoji(`The answer is ${mathResult}.`);
    }

    // 4. Dataset Knowledge
    const knowledgeResult = searchDataset(command);
    if (knowledgeResult) return addEmoji(knowledgeResult);

    return null; // No local match, fallback to server
};
