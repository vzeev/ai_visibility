const jobs = [
  { prompt: "Brandlight comparison", model: "gpt-5-main", status: "running", tries: "1/3" },
  { prompt: "Visibility platforms", model: "gpt-5-mini", status: "queued", tries: "0/3" },
  { prompt: "Citation scan", model: "o-series-reasoning", status: "throttled", tries: "1/3" }
];

export function QueuePanel() {
  return (
    <section className="content-grid">
      <div className="metric-card">
        <span>Pending</span>
        <strong>18</strong>
      </div>
      <div className="metric-card">
        <span>Running</span>
        <strong>3</strong>
      </div>
      <div className="metric-card">
        <span>Throttled</span>
        <strong>2</strong>
      </div>
      <div className="metric-card">
        <span>Succeeded</span>
        <strong>126</strong>
      </div>

      <div className="panel span-3">
        <div className="panel-header">
          <h2>Visibility queue</h2>
          <button type="button">Refresh</button>
        </div>
        <table>
          <thead>
            <tr>
              <th>Prompt</th>
              <th>Model</th>
              <th>Status</th>
              <th>Attempts</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={`${job.prompt}-${job.model}`}>
                <td>{job.prompt}</td>
                <td>{job.model}</td>
                <td>
                  <span className={`badge ${job.status}`}>{job.status}</span>
                </td>
                <td>{job.tries}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
