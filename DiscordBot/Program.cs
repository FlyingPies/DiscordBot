using Discord;
using Discord.Commands;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Google.Apis.Customsearch.v1.Data;
using Google.Apis.Customsearch.v1;
using System.IO;
using Discord.Audio;
using System.Threading;
using System.Diagnostics;
using System.Drawing;

namespace DiscordBot
{

    class Program
    {
        static void Main(string[] args)
        {
            new Program().Start();

        }
        private DiscordClient _client;
        private Dictionary<User, Boolean> hasVoted;
        private Dictionary<User, int> votesAgainst;
        public void Start()
        {
            _client = new DiscordClient(x =>
            {
                x.AppName = "Discord Bot";
                x.AppUrl = "";
                x.LogLevel = LogSeverity.Info;
                x.LogHandler = Log;
            });
            hasVoted = new Dictionary<User, Boolean>();
            votesAgainst = new Dictionary<User, int>();
            _client.UsingCommands(x =>
           {
               x.PrefixChar = '!';
               x.AllowMentionPrefix = false;
               x.HelpMode = HelpMode.Public;
           });
            _client.UsingAudio(x => // Opens an AudioConfigBuilder so we can configure our AudioService
            {
                x.Mode = AudioMode.Outgoing; // Tells the AudioService that we will only be sending audio
            });
            var token = "MjA3NjQ1MjA2OTE5NTEyMDY0.CnmIKw.5AXAwtsEpQhpJw91zNWWdorNNFQ";
            CreateCommands();
            _client.ExecuteAndWait(async () =>
            {
                await _client.Connect(token);
                _client.SetGame("lego legends");
                Thread.Sleep(500);
                var voiceChannel = _client.FindServers("lol").FirstOrDefault().VoiceChannels.FirstOrDefault(); // Finds the first VoiceChannel on the server 'Music Bot Server'

                var _vClient = await _client.GetService<AudioService>() // We use GetService to find the AudioService that we installed earlier. In previous versions, this was equivelent to _client.Audio()
                        .Join(voiceChannel); // Join the Voice Channel, and return the IAudioClient.

            });
        }

        public void CreateCommands()
        {
            var cService = _client.GetService<CommandService>();
            _client.UserJoined += async (s, e) =>
            {
                if (e.User != e.Server.FindUsers("DiscordBot").FirstOrDefault())
                {
                    await e.Server.DefaultChannel.SendMessage(e.User.Mention + " has joined the server for the first time!\nSay !rules for rules.\nIf you have any questions about anything ask " + e.Server.FindUsers("FlyingPies").FirstOrDefault().Mention + ".");
                }
            };
            cService.CreateCommand("ping") //basic message detection
                .Description("returns \"pong\"")
                .Do(async (e) =>
                {
                    await e.Channel.SendMessage("pong");
                });
            cService.CreateCommand("hello") //basic argument detection
                .Description("Welcomes a user")
                .Parameter("user", ParameterType.Unparsed)
                .Do(async (e) =>
                {
                    var toReturn = $"Hello {e.GetArg("user")}";
                    await e.Channel.SendMessage(toReturn);
                });
            cService.CreateCommand("send_file") // file sending
                .Description("Sends a file")
                .Do(async (e) =>
                {
                    await e.Channel.SendFile("cat.jpg");
                    await e.Channel.SendMessage("file sent");
                });
            cService.CreateCommand("clearchat") //clear chat. admin only
                .Description("Clears the chat\nAdmin only")
                .Do(async (e) =>
                {
                    if (e.Message.User.HasRole(e.Server.FindRoles("Admin").FirstOrDefault()))
                    {
                        var msgs = (await e.Channel.DownloadMessages(100).ConfigureAwait(false));
                        foreach (var m in msgs)
                        {
                            try
                            {
                                await m.Delete().ConfigureAwait(false);
                            }
                            catch { }
                            await Task.Delay(100).ConfigureAwait(false);
                        }
                    }
                    else
                        await e.Channel.SendMessage(e.User.Mention + " does not have access to this command.");
                });
            cService.CreateCommand("vote_kick") //vote kick
                .Description("Starts a vote kick to kick a mentioned user from the server")
                .Parameter("Mentioned User", ParameterType.Required)
                .Do(async (e) =>
                {
                    User s = e.Message.MentionedUsers.FirstOrDefault();

                    if (s == null)
                        await e.Channel.SendMessage("There is no such user in the server");

                    else
                    {
                        if (s.HasRole(e.Server.FindRoles("Admin").FirstOrDefault()) || s.HasRole(e.Server.FindRoles("BOT").FirstOrDefault()))
                            await e.Channel.SendMessage("This person cannot be kicked");
                        else {
                            if (!votesAgainst.ContainsKey(s))
                                votesAgainst.Add(s, 0);
                            if (votesAgainst[s] == 0)
                            {

                                await e.Channel.SendMessage("A vote kick has been started by " + e.Message.User.Mention + " against " + s.Mention + ". " + (((OnlineUserCount(e.Server) - 1) / 2 + 1) - votesAgainst[s]) + " more votes are needed to kick " + s.Mention + ".");
                                foreach (var user in e.Server.Users)
                                {
                                    if (hasVoted.ContainsKey(user))
                                        hasVoted.Remove(user);
                                    hasVoted.Add(user, false);
                                }
                                hasVoted[e.Message.User] = true;
                                votesAgainst[s] += 1;
                            }
                            else if (votesAgainst[s] == ((OnlineUserCount(e.Server) - 1) / 2 + 1) - 1)
                            {
                                await e.Channel.SendMessage("Vote Kick has Succeeded. Kicking " + s.Mention + ".....");
                                await s.Kick();
                                votesAgainst[s] = 0;
                            }
                            else if (votesAgainst[s] > 0)
                            {
                                if (hasVoted[e.Message.User])
                                    await e.Channel.SendMessage("You have already voted.");
                                else
                                {
                                    hasVoted[e.Message.User] = true;
                                    votesAgainst[s] += 1;
                                    await e.Channel.SendMessage(e.Message.User.Mention + " has voted to kick " + s.Mention + ". Only " + (((OnlineUserCount(e.Server) - 1) / 2 + 1) - votesAgainst[s]) + " more votes are needed to kick " + s.Mention);
                                    if (votesAgainst[s] >= ((OnlineUserCount(e.Server) - 1) / 2 + 1))
                                    {
                                        await e.Channel.SendMessage("Vote Kick has Succeeded. Kicking " + s.Mention + ".....");
                                        await s.Kick();
                                        votesAgainst[s] = 0;
                                    }
                                }

                            }
                        }
                    }
                });
            cService.CreateCommand("rules") //rules
                .Description("Gives the server rules")
                .Do(async (e) =>
                {
                    await e.Channel.SendMessage("No rules.\nFor now...");
                });
            cService.CreateCommand("google") //google
                .Description("Provides the top google result of the search query")
                .Parameter("query", ParameterType.Unparsed)
                .Do(async (e) =>
                {
                    string query = e.GetArg("query");
                    const string apiKey = "AIzaSyCaoKYbfX2TdeWTtojigK-btjNBh1qlZjs";
                    const string searchEngineId = "013388782467450060570:cc_bo6ma8uk";
                    CustomsearchService customSearchService = new CustomsearchService(new Google.Apis.Services.BaseClientService.Initializer() { ApiKey = apiKey });
                    Google.Apis.Customsearch.v1.CseResource.ListRequest listRequest = customSearchService.Cse.List(query);
                    listRequest.Cx = searchEngineId;
                    Search search = listRequest.Execute();
                    await e.Channel.SendMessage(search.Items.FirstOrDefault().Link + "");
                });
            cService.CreateCommand("play") //play
                .Description("plays requested song.\nSong must be on Youtube or SoundCloud")
                .Parameter("query", ParameterType.Unparsed)
                .Do(async (e) =>
                {
                    var voiceChannel = e.User.VoiceChannel;


                    string query = e.GetArg("query");
                    const string apiKey = "AIzaSyCaoKYbfX2TdeWTtojigK-btjNBh1qlZjs";
                    const string searchEngineId = "013388782467450060570:2jw06f1dfj4";
                    CustomsearchService customSearchService = new CustomsearchService(new Google.Apis.Services.BaseClientService.Initializer() { ApiKey = apiKey });
                    Google.Apis.Customsearch.v1.CseResource.ListRequest listRequest = customSearchService.Cse.List(query);
                    listRequest.Cx = searchEngineId;
                    Search search = listRequest.Execute();
                    string link = search.Items.FirstOrDefault().Link;
                    await e.Channel.SendMessage(link);
                    string output = "";
                    if (link.Contains("youtube")) { 
                    var proc = Process.Start(new ProcessStartInfo
                    { // FFmpeg requires us to spawn a process and hook into its stdout, so we will create a Process
                        FileName = "youtube-dl",
                        Arguments = $"-f m4a " + link,
                        UseShellExecute = false,
                        RedirectStandardOutput = true
                    });
                        while (true)
                        {
                            output = proc.StandardOutput.ReadLine();
                            if (output.Contains("download"))
                            {
                                output = output.Substring(11, output.IndexOf(".m4a") - 6);
                                break;
                            }
                        }
                    }
                    else if(link.Contains("soundcloud"))
                    {
                        var proc = Process.Start(new ProcessStartInfo
                        { // FFmpeg requires us to spawn a process and hook into its stdout, so we will create a Process
                            FileName = "youtube-dl",
                            Arguments = $"-f mp3 " + link,
                            UseShellExecute = false,
                            RedirectStandardOutput = true
                        });
                        while (true)
                        {
                            output = proc.StandardOutput.ReadLine();
                            if (output.Contains("download"))
                            {
                                output = output.Substring(11, output.IndexOf(".mp3") - 6);
                                break;
                            }
                        }
                    }

                    Console.WriteLine(output);
                    string filePath = @"C:\Users\Arjun\Documents\Visual Studio 2015\Projects\DiscordBot\DiscordBot\bin\Debug\" + output;
                    var _vClient = await _client.GetService<AudioService>() // We use GetService to find the AudioService that we installed earlier. In previous versions, this was equivelent to _client.Audio()
                        .Join(voiceChannel); // Join the Voice Channel, and return the IAudioClient.
                    if (voiceChannel == null)
                    {
                        await e.Channel.SendMessage("Please join a voice channel");
                        return;
                    }
                  var process = await Task.Run(() =>Process.Start(new ProcessStartInfo
                    { // FFmpeg requires us to spawn a process and hook into its stdout, so we will create a Process
                        FileName = "ffmpeg",
                        Arguments = $"-i \"{filePath}\" " + // Here we provide a list of arguments to feed into FFmpeg. -i means the location of the file/URL it will read from
                        "-f s16le -ar 48000 -ac 2 pipe:1", // Next, we tell it to output 16-bit 48000Hz PCM, over 2 channels, to stdout.
                        UseShellExecute = false,
                        RedirectStandardOutput = true // Capture the stdout of the process
                    }));
                    Thread.Sleep(2000); // Sleep for a few seconds to FFmpeg can start processing data.

                    int blockSize = 3840; // The size of bytes to read per frame; 1920 for mono
                    byte[] buffer = new byte[blockSize];
                    int byteCount;

                    while (true) // Loop forever, so data will always be read
                    {
                        byteCount = process.StandardOutput.BaseStream // Access the underlying MemoryStream from the stdout of FFmpeg
                                .Read(buffer, 0, blockSize); // Read stdout into the buffer

                        if (byteCount == 0) // FFmpeg did not output anything
                            break; // Break out of the while(true) loop, since there was nothing to read.

                         _vClient.Send(buffer, 0, byteCount); // Send our data to Discord
                    }
                    _vClient.Wait(); // Wait for the Voice Client to finish sending data, as ffMPEG may have already finished buffering out a song, and it is unsafe to return now.

                });

            cService.CreateCommand("skip")
                .Description("Skips the current song")
                .Do(async (e) =>
                {
                    if (Process.GetProcessesByName("ffmpeg") != null)
                    {
                        Process[] process = Process.GetProcessesByName("ffmpeg");
                        process[0].Kill();
                        await e.Channel.SendMessage("Song has been skipped");
                    }
                    else
                        await e.Channel.SendMessage("No song is playing");

                });
           }
        
        public void Log(object send, LogMessageEventArgs e)
        {
            Console.WriteLine($"[{e.Severity}][{e.Source}] {e.Message}");
            // [INFO] [Discord] Client Connected
        }

        public int OnlineUserCount(Server s)
        {
            int cnt = 0;
            foreach( var item in s.Users)
            {
                if (item.Status == "Online")
                    cnt++;
            }
            return cnt;
        }

    }

}


