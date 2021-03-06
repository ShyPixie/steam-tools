#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2016
#
# The Steam Tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The Steam Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

import stlib

current_badge = 0

def remove_completed_badges(badges):
    stlib.logger.info('Ignoring already completed badges')
    new_badges = []
    for badge in badges:
        if get_card_count(badge) != 0:
            new_badges.append(badge)

    return new_badges


def get_badge_page_count():
    stlib.logger.info('Counting badge pages')
    profile = stlib.steam_profile()
    html = stlib.network.try_get_html('steam', '{}/badges/'.format(profile))

    try:
        page_count = int(html.findAll('a', class_='pagelink')[-1].text)
    except IndexError:
        page_count = 1

    return page_count


def get_badges(page):
    stlib.logger.info('Getting badges from page %d', page)
    profile = stlib.steam_profile()
    html = stlib.network.try_get_html('steam', '{}/badges/?p={}'.format(profile, page))

    return html.findAll('div', class_='badge_title_row')


def get_game_name(badge):
    stlib.logger.verbose('Getting game name')
    title = badge.find('div', class_='badge_title')

    return title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1]


def get_game_id(badge):
    stlib.logger.verbose('Getting game id')

    try:
        game_href = badge.find('a')['href']
    except TypeError:
        # FIXME: It's a foil badge. The game id is above the badge_title_row...
        return str(000000)

    try:
        game_id = game_href.split('/', 3)[3]
    except IndexError:
        # Possibly a game without cards
        # TODO: This can speed up the remove_completed_badges?
        game_id = game_href.split('_', 6)[4]

    return str(game_id)


def get_card_count(badge, update_from_web=False):
    game_name = get_game_name(badge)
    game_id = get_game_id(badge)

    if update_from_web:
        stlib.logger.verbose('Updating number of cards of %s(%s)', game_name, game_id)
        profile = stlib.steam_profile()
        html = stlib.network.try_get_html('steam', '{}/gamecards/{}'.format(profile, game_id))
        stats = html.find('div', class_='badge_title_stats_drops')
        progress = stats.find('span', class_='progress_info_bold')
    else:
        stlib.logger.verbose('Getting number of cards of %s(%s)', game_name, game_id)
        progress = badge.find('span', class_='progress_info_bold')

    if not progress or 'No' in progress.text:
        return 0
    else:
        return int(progress.text.split(' ', 3)[0])


def get_cards_info():
    stlib.logger.info('Getting cards info')
    cards_info = {k: [] for k in ['game_name', 'card_count', 'badge_price']}
    html = stlib.network.get_html('http://www.steamcardexchange.net/index.php?badgeprices')

    for info in html.findAll('tr')[1:]:
        cards_info['game_name'].append(info.find('a').text)
        cards_info['card_count'].append(int(info.findAll('td')[1].text))
        cards_info['badge_price'].append(float(info.findAll('td')[2].text[1:]))

    return cards_info


def get_badge_price(cards_info, badge):
    game_name = get_game_name(badge)
    stlib.logger.verbose('Getting badge price for %s', game_name)

    try:
        price_index = cards_info['game_name'].index(game_name)
        return cards_info['badge_price'][price_index]
    except ValueError:
        return 0


def get_badge_cards_count(cards_info, badge):
    game_name = get_game_name(badge)
    stlib.logger.info('Getting cards count for %s', game_name)
    return cards_info['card_count'][cards_info['game_name'].index(game_name)]


def get_total_card_count(badges):
    card_count = 0
    for badge in badges:
        card_count += get_card_count(badge)
        yield card_count


def order_by_most_valuable(cards_info, badges):
    stlib.logger.info("Ordering by most valuable")
    prices = [get_badge_price(cards_info, badge) for badge in badges]
    badges_count = len(badges)
    badges_order = sorted(range(badges_count),
                          key=lambda key: prices[key],
                          reverse=True)
    ordered_badges = []

    for _ in prices:
        ordered_badges = [badges[index] for index in badges_order]

    return ordered_badges
