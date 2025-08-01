# **App Name**: DataWise Dashboard

## Core Features:

- Authentication: Authentication flow with login and signup pages, redirecting to a protected dashboard.
- Dashboard Layout: Dashboard layout with a sidebar for navigation, header displaying session info, and protected routes.
- SQL Query Panel: SQL Query Panel: Allows users to type SQL queries and display results in a table format.
- LLM Prompt Panel: LLM Prompt Panel: A text area where users can input natural language prompts to query an AI; the LLM will use a 'tool' to help decide whether or not include sample database entries, which will inform the LLM about the database, and let the LLM generate its natural language response based on the request and these samples. Response shown in a display box.
- Charts Panel: Charts Panel: Displays data visualizations using Recharts (BarChart, LineChart) from mock API data.
- State Management (Zustand): Use Zustand for UI toggles, filters, or client state, such as managing selected tabs.
- State Management (React Query): Employ React Query for backend/API data fetching and state management of server data.

## Style Guidelines:

- Primary color: Use a vibrant purple (#A06CD5) to convey innovation and insight in data analysis. 
- Background color: Implement a dark background (#1A1A1D) to provide a professional, modern feel with reduced eye strain, complementary to the vibrant purple.
- Accent color: Use a muted blue (#70A0D0) for interactive elements and highlights, creating a balanced interface.
- Body and headline font: Use 'Inter' (sans-serif) for a modern, neutral, and readable text.
- Code font: Use 'Source Code Pro' (monospace) for displaying code snippets.
- Utilize a responsive layout using Tailwind Grid/Flex to adapt to different screen sizes.
- Apply subtle transitions and animations to enhance user interaction, like loading states for data fetching.