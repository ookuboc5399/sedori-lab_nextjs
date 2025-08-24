
import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { url } = body;

    if (!url) {
      return NextResponse.json({ error: 'URL is required' }, { status: 400 });
    }

    // Basic URL validation
    try {
      new URL(url);
    } catch (_) {
      return NextResponse.json({ error: 'Invalid URL format' }, { status: 400 });
    }

    // Path to the Python script and virtual environment
    const projectRoot = process.cwd();
    const venvPython = path.join(projectRoot, '.venv', 'bin', 'python');
    const scriptPath = path.join(projectRoot, 'scripts', 'scrape_mercari.py');

    // Command to execute
    const command = `${venvPython} ${scriptPath} "${url}"`;

    return new Promise((resolve) => {
      exec(command, (error, stdout, stderr) => {
        if (error) {
          console.error(`Execution error: ${error.message}`);
          // Try to parse stderr for a more specific error from the script
          try {
              const scriptError = JSON.parse(stderr);
              resolve(NextResponse.json({ error: scriptError.error || 'Script execution failed' }, { status: 500 }));
          } catch (e) {
              resolve(NextResponse.json({ error: 'Script execution failed and could not parse error output.' }, { status: 500 }));
          }
          return;
        }

        if (stderr) {
            try {
                const scriptError = JSON.parse(stderr);
                console.warn(`Script stderr:`, scriptError);
                resolve(NextResponse.json({ error: scriptError.error || 'An error occurred in the script' }, { status: 400 }));
            } catch (e) {
                console.warn(`Non-JSON stderr: ${stderr}`);
                resolve(NextResponse.json({ error: 'An unknown error occurred in the script' }, { status: 500 }));
            }
            return;
        }

        try {
          const result = JSON.parse(stdout);
          resolve(NextResponse.json(result, { status: 200 }));
        } catch (e) {
          console.error('Error parsing script output:', e);
          resolve(NextResponse.json({ error: 'Failed to parse scraper output' }, { status: 500 }));
        }
      });
    });

  } catch (e) {
    console.error('API route error:', e);
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 });
  }
}
