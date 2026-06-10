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

    private SqliteConnection? _connection;

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseSetting("APPLY_MIGRATIONS", "false");
        builder.UseEnvironment("Testing");
        builder.UseSetting("ConnectionStrings:DefaultConnection", SharedSqliteConnectionString);

        _connection = new SqliteConnection(SharedSqliteConnectionString);
        _connection.Open();
    }

    protected override IHost CreateHost(IHostBuilder builder)
    {
        var host = base.CreateHost(builder);

        using var scope = host.Services.CreateScope();
        scope.ServiceProvider.GetRequiredService<ApplicationDbContext>().Database.EnsureCreated();

        return host;
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing)
            _connection?.Dispose();

        base.Dispose(disposing);
    }
}
