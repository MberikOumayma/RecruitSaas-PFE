using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.StaticFiles;
using Recrutement_api.Configuration;
using Recrutement_api.Data;
using Recrutement_api.DTOs;
using Recrutement_api.Extensions;
using Recrutement_api.Services;
using Recrutement_api.Services.CandidatServices;
using Recrutement_api.Services.CandidateServices;
using Recrutement_api.Services.Expert;
using Recrutement_api.Services.Expert.Implementations;
using Recrutement_api.Services.Implementations;
using Recrutement_api.Services.Interfaces;
using Recrutement_api.Services.Shared;
using Recrutement_api.Services.TenantServices;
using Recrutement_api.Services.AI;

var builder = WebApplication.CreateBuilder(args);

// Clés OAuth (Google / Facebook / LinkedIn) — fichier local non versionné
var socialAuthFile = Path.Combine(builder.Environment.ContentRootPath, "appsettings.SocialAuth.json.example");
if (File.Exists(socialAuthFile))
    builder.Configuration.AddJsonFile("appsettings.SocialAuth.json.example", optional: true, reloadOnChange: true);

// Services
builder.Services.Configure<EmailSettings>(builder.Configuration.GetSection("EmailSettings"));
builder.Services.Configure<CloudinarySettings>(builder.Configuration.GetSection("CloudinarySettings"));

builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
    if (builder.Environment.IsEnvironment("Testing"))
        options.UseSqlite(connectionString);
    else
        options.UseNpgsql(connectionString);
});

// CV Extraction
builder.Services.AddHttpClient();
builder.Services.AddScoped<Recrutement_api.Services.CvExtraction.Extractors.PdfTextExtractor>();
builder.Services.AddScoped<Recrutement_api.Services.CvExtraction.Extractors.DocxTextExtractor>();
builder.Services.AddHttpClient<Recrutement_api.Services.CvExtraction.AiCvTextExtractor>();
builder.Services.AddScoped<Recrutement_api.Services.CvExtraction.ICvExtractionService, Recrutement_api.Services.CvExtraction.CvExtractionService>();

// CORS
var corsOrigins = new List<string>
{
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8888",
    "http://localhost:3000",
    "https://localhost:5173"
};
var frontendUrl = builder.Configuration["Frontend:Url"];
if (!string.IsNullOrWhiteSpace(frontendUrl) && !corsOrigins.Contains(frontendUrl))
    corsOrigins.Add(frontendUrl);

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
        policy.WithOrigins(corsOrigins.ToArray())
        .AllowAnyHeader()
        .AllowAnyMethod()
        .AllowCredentials()
    );
});

// Controllers
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.CamelCase;
        options.JsonSerializerOptions.PropertyNameCaseInsensitive = true;
        options.JsonSerializerOptions.Converters
            .Add(new System.Text.Json.Serialization.JsonStringEnumConverter());
    });

builder.Services.AddEndpointsApiExplorer();

builder.Services.AddSwaggerGen(c =>
{
    c.AddSecurityDefinition("Bearer", new Microsoft.OpenApi.Models.OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = Microsoft.OpenApi.Models.SecuritySchemeType.ApiKey,
        Scheme = "Bearer",
        BearerFormat = "JWT",
        In = Microsoft.OpenApi.Models.ParameterLocation.Header,
        Description = "Entrez: Bearer {votre_token}"
    });

    c.AddSecurityRequirement(new Microsoft.OpenApi.Models.OpenApiSecurityRequirement
    {
        {
            new Microsoft.OpenApi.Models.OpenApiSecurityScheme
            {
                Reference = new Microsoft.OpenApi.Models.OpenApiReference
                {
                    Type = Microsoft.OpenApi.Models.ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            new string[] {}
        }
    });
});

// Services métier
builder.Services.AddHttpContextAccessor();
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<IJwtService, JwtService>();
builder.Services.AddScoped<ICurrentUserService, CurrentUserService>();
builder.Services.AddScoped<ILinkGeneratorService, LinkGeneratorService>();
builder.Services.AddScoped<IOffreService, OffreService>();
builder.Services.AddScoped<IExpertService, ExpertFonctionsService>();
builder.Services.AddScoped<ICandidatService, CandidatService>();

builder.Services.AddScoped<TenantService>();
builder.Services.AddScoped<AdminService>();
builder.Services.AddScoped<CandidatureService>();
builder.Services.AddScoped<ITeamService, TeamService>();

builder.Services.AddTalentFlowAuthentication(builder.Configuration);

builder.Services.AddScoped<Recrutement_api.Services.Expert.ExpertService>();
builder.Services.AddScoped<EmailService>();
builder.Services.AddSingleton<EmailQueueService>();
builder.Services.AddHostedService(sp => sp.GetRequiredService<EmailQueueService>());

builder.Services.AddScoped<IExpertService, ExpertUserService>();
builder.Services.AddScoped<CandidateProfileService>();
builder.Services.AddScoped<TenantProfileService>();
builder.Services.AddScoped<IAiOrchestratorService, AiOrchestratorService>();
builder.Services.AddScoped<ISavedJobService, SavedJobService>();
builder.Services.AddScoped<NotificationService>();

builder.Services.AddScoped<Recrutement_api.Services.Entretien.IEntretienService, Recrutement_api.Services.Entretien.EntretienService>();
builder.Services.AddScoped<Recrutement_api.Services.Quiz.IQuizService, Recrutement_api.Services.Quiz.QuizService>();

builder.Services.AddScoped<Recrutement_api.Services.TenantServices.ReportService>();

// ✅ CORRECTION : builder.Build() doit être appelé ICI, après tous les services
var app = builder.Build();

if (string.Equals(builder.Configuration["APPLY_MIGRATIONS"], "true", StringComparison.OrdinalIgnoreCase))
{
    using var scope = app.Services.CreateScope();
    scope.ServiceProvider.GetRequiredService<ApplicationDbContext>().Database.Migrate();
}

// Swagger
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// 1. CORS
app.UseCors("AllowFrontend");

// 2. Static files (GLB support)
var webRoot = app.Environment.WebRootPath
    ?? Path.Combine(app.Environment.ContentRootPath, "wwwroot");

if (!Directory.Exists(webRoot))
    Directory.CreateDirectory(webRoot);

var provider = new FileExtensionContentTypeProvider();
provider.Mappings[".glb"] = "model/gltf-binary";

app.UseStaticFiles(new StaticFileOptions
{
    ContentTypeProvider = provider,
    OnPrepareResponse = ctx =>
    {
        var path = ctx.File.Name?.ToLowerInvariant() ?? "";
        if (!path.EndsWith(".jpg") && !path.EndsWith(".jpeg") && !path.EndsWith(".png") && !path.EndsWith(".webp") && !path.EndsWith(".jfif"))
            return;
        var origin = ctx.Context.Request.Headers.Origin.ToString();
        if (origin is "http://localhost:5173" or "http://localhost:8080" or "http://localhost:8081" or "http://localhost:8888" or "http://localhost:3000")
            ctx.Context.Response.Headers["Access-Control-Allow-Origin"] = origin;
    }
});

// 3. Auth
app.UseAuthentication();
app.UseAuthorization();

// Health check
app.MapGet("/health", () => Results.Ok(new
{
    Status = "Healthy",
    Timestamp = DateTime.UtcNow
}));

app.MapControllers();

app.Run();

public partial class Program { }