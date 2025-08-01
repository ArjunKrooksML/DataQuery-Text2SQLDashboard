'use server';
/**
 * @fileOverview A LLM query AI agent that uses a tool to optionally include database entries to inform the LLM's natural language response.
 *
 * - llmQueryWithDatabase - A function that handles the LLM query process.
 * - LlmQueryWithDatabaseInput - The input type for the llmQueryWithDatabase function.
 * - LlmQueryWithDatabaseOutput - The return type for the llmQueryWithDatabase function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const LlmQueryWithDatabaseInputSchema = z.object({
  prompt: z.string().describe('The natural language prompt to query the AI.'),
});
export type LlmQueryWithDatabaseInput = z.infer<typeof LlmQueryWithDatabaseInputSchema>;

const LlmQueryWithDatabaseOutputSchema = z.object({
  response: z.string().describe('The natural language response from the AI.'),
});
export type LlmQueryWithDatabaseOutput = z.infer<typeof LlmQueryWithDatabaseOutputSchema>;

export async function llmQueryWithDatabase(input: LlmQueryWithDatabaseInput): Promise<LlmQueryWithDatabaseOutput> {
  return llmQueryWithDatabaseFlow(input);
}

const getSampleDatabaseEntries = ai.defineTool(
  {
    name: 'getSampleDatabaseEntries',
    description: 'Returns sample entries from the database to provide context for the LLM.',
    inputSchema: z.object({
      prompt: z.string().describe('The natural language prompt to guide the selection of relevant database entries.'),
    }),
    outputSchema: z.array(z.string()).describe('Sample database entries relevant to the prompt.'),
  },
  async (input) => {
    // Mock implementation: Replace with actual database query logic
    const sampleEntries = [
      'Entry 1: Customer Name - John Doe, Order ID - 12345, Product - Widget',
      'Entry 2: Customer Name - Jane Smith, Order ID - 67890, Product - Gadget',
      'Entry 3: Customer Name - David Lee, Order ID - 24680, Product - Thingamajig',
    ];

    // Simulate filtering based on the prompt (very basic)
    const filteredEntries = sampleEntries.filter(entry => entry.toLowerCase().includes(input.prompt.toLowerCase()));

    return filteredEntries;
  }
);

const llmQueryWithDatabasePrompt = ai.definePrompt({
  name: 'llmQueryWithDatabasePrompt',
  tools: [getSampleDatabaseEntries],
  input: {schema: LlmQueryWithDatabaseInputSchema},
  output: {schema: LlmQueryWithDatabaseOutputSchema},
  prompt: `You are an AI assistant that answers questions based on the provided context.

  The user will provide a natural language prompt, and you should generate a natural language response.

  You have access to a tool called 'getSampleDatabaseEntries' that can provide sample database entries relevant to the prompt.
  Use this tool if the prompt seems like it could be answered using information about a database.

  Prompt: {{{prompt}}}

  {{#if tools.getSampleDatabaseEntries}}
  Sample Database Entries:
  {{#each tools.getSampleDatabaseEntries}}
  - {{{this}}}
  {{/each}}
  {{/if}}
  `,
});

const llmQueryWithDatabaseFlow = ai.defineFlow(
  {
    name: 'llmQueryWithDatabaseFlow',
    inputSchema: LlmQueryWithDatabaseInputSchema,
    outputSchema: LlmQueryWithDatabaseOutputSchema,
  },
  async input => {
    const {output} = await llmQueryWithDatabasePrompt(input);
    return output!;
  }
);
