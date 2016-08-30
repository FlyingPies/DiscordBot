using Discord;
using Discord.Commands;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using Google.Apis.Customsearch.v1;
using System.Threading.Tasks;
using Google.Apis.Customsearch.v1.Data;
// This is all deprecated code. Please see Program.cs for the latest version
namespace DiscordBot
{

    class DiscordBot
    {
        private DiscordClient bot;
        private Dictionary<User, Boolean> hasVoted;
        private Dictionary<User, int> votesAgainst;
        public DiscordBot(string user,string pass)
        {
            bot = new DiscordClient();
            hasVoted = new Dictionary<User, Boolean>();
            votesAgainst = new Dictionary<User, int>();
            bot.MessageReceived += Bot_MessageReceived;
            /* completed
            bot.UserJoined += async (s, e) => {
                if(e.User!=e.Server.FindUsers("DiscordBot").FirstOrDefault())
                {
                    await e.Server.DefaultChannel.SendMessage(e.User.Mention+" has joined the server for the first time!\nSay !rules for rules.\nIf you have any questions about anything ask"+e.Server.FindUsers("FlyingPies").FirstOrDefault().Mention+".");
                }
            };
            */
            bot.Connect(user, pass);
        }
        private async void Bot_MessageReceived(object sender, MessageEventArgs e)
        {
 
            if (e.Message.IsAuthor) return;
            else {
                /* completed
                if (e.Message.Text.ToLower() == "!clearchat")
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

                }
                */

                /* COMPLETED
                if (e.Message.Text.ToLower() == "!help")
                {
                    await e.Channel.SendMessage("!clearchat - Clears the chat (ADMIN ONLY)\n!votekick - Starts a vote kick to kick a user from the server\n!google - Googles something for you");
                }


                */

                /*  COMPLETED
                if (e.Message.Text.Length > 10 && e.Message.Text.Substring(0, 9) == "!votekick")
                {

                    string accused = e.Message.Text.Substring(11);
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

                                await e.Channel.SendMessage("A vote kick has been started by " + e.Message.User.Mention + " against " + s.Mention + ". " + (((e.Server.UserCount - 1) / 2 + 1)-votesAgainst[s]) + " more votes are needed to kick " + s.Mention + ".");
                                foreach (var user in e.Server.Users)
                                {
                                    if (hasVoted.ContainsKey(user))
                                        hasVoted.Remove(user);
                                    hasVoted.Add(user, false);
                                }
                                hasVoted[e.Message.User] = true;
                                votesAgainst[s] += 1;
                            }
                            else if (votesAgainst[s] == ((e.Server.UserCount - 1) / 2 + 1) - 1)
                            {
                                await e.Channel.SendMessage("Vote Kick has Succeeded. Kicking " + s.Mention + ".....");
                                await s.Kick();
                                votesAgainst[s] = 0;
                            }
                            else if (votesAgainst[s] > 0)
                            {
                                if (hasVoted[e.Message.User])
                                    await e.Channel.SendMessage("This user has already voted.");
                                else
                                {
                                    hasVoted[e.Message.User] = true;
                                    votesAgainst[s] += 1;
                                    await e.Channel.SendMessage(e.Message.User.Mention + " has voted to kick" + s.Mention + ". Only " + (((e.Server.UserCount - 1) / 2 + 1) - votesAgainst[s]) + " more votes are needed to kick " + s.Mention);
                                    if (votesAgainst[s] >= ((e.Server.UserCount - 1) / 2 + 1))
                                    {
                                        await e.Channel.SendMessage("Vote Kick has Succeeded. Kicking " + s.Mention + ".....");
                                        await s.Kick();
                                        votesAgainst[s] = 0;
                                    }
                                }

                            }
                        }
                    }
                }
                */

                /* COMPLETED
                if (e.Message.Text == "!rules")
                {
                    await e.Channel.SendMessage("No rules.\nFor now...");
                }

                */

                /* COMPLETED
                if (e.Message.Text.Length > 7&&e.Message.Text.Substring(0,7) == "!google")
                {
                    string word = e.Message.Text.Substring(8);
                    const string apiKey = "AIzaSyCaoKYbfX2TdeWTtojigK-btjNBh1qlZjs";
                    const string searchEngineId = "013388782467450060570:cc_bo6ma8uk";
                    string query = word;
                    CustomsearchService customSearchService = new CustomsearchService(new Google.Apis.Services.BaseClientService.Initializer() { ApiKey = apiKey });
                    Google.Apis.Customsearch.v1.CseResource.ListRequest listRequest = customSearchService.Cse.List(query);
                    listRequest.Cx = searchEngineId;
                    Search search = listRequest.Execute();
                    word = word.Replace("%", "%25");
                    word = word.Replace("!", "%21");
                    word = word.Replace("\"", "%22");
                    word = word.Replace("#", "%23");
                    word = word.Replace("&", "%26");
                    word = word.Replace("'", "%27");
                    word = word.Replace("(", "%28");
                    word = word.Replace(")", "%29");
                    word = word.Replace("*", "%2A");
                    word = word.Replace("+", "%2B");
                    word = word.Replace(",", "%2C");
                    word = word.Replace("-", "%2D");
                    word = word.Replace(".", "%2E");
                    word = word.Replace("/", "%2F");
                    word = word.Replace("<", "%3C");
                    word = word.Replace("=", "%3D");
                    word = word.Replace(">", "%3E");
                    word = word.Replace(" ", "+");
                    await e.Channel.SendMessage(search.Items.FirstOrDefault().Link+"");
                }
                */

            }
        }

    }

}
