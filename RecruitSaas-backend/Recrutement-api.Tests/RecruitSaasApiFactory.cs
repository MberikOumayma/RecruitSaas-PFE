using System.Data;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Recrutement_api.Data;

namespace Recrutement_api.Tests;

public class RecruitSaasApiFactory : WebApplicationFactory<Program>
{
    private const string SharedSqliteConnectionString =
        "Data Source=RecruitSaasTestDb;Mode=Memory;Cache=Shared";

    private static readonly object DbInitLock = new();
    private static bool _databaseInitialized;
    private static SqliteConnection? _keepAliveConnection;

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseSetting("APPLY_MIGRATIONS", "false");
        builder.UseEnvironment("Testing");
        builder.UseSetting("ConnectionStrings:DefaultConnection", SharedSqliteConnectionString);

        lock (DbInitLock)
        {
            _keepAliveConnection ??= new SqliteConnection(SharedSqliteConnectionString);
            if (_keepAliveConnection.State != ConnectionState.Open)
                _keepAliveConnection.Open();
        }
    }

    protected override IHost CreateHost(IHostBuilder builder)
    {
        var host = base.CreateHost(builder);

        lock (DbInitLock)
        {
            if (!_databaseInitialized)
            {
                using var scope = host.Services.CreateScope();
                scope.ServiceProvider.GetRequiredService<ApplicationDbContext>().Database.EnsureCreated();
                _databaseInitialized = true;
            }
        }

        return host;
    }

    protected override void Dispose(bool disposing)
    {
        // Shared in-memory SQLite stays open for the full test run via _keepAliveConnection.
        base.Dispose(disposing);
    }
}
